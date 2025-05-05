# Analyse de données
import pandas as pd
import numpy as np
from datetime import datetime
# Visualisation
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.plotting import scatter_matrix
# Standardisation
from sklearn.preprocessing import StandardScaler
# Modélisation
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import StratifiedShuffleSplit
# métriques
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# Historique
import os

# Lecture des données
DATA_PATH = 'data/carData_cleaned.csv'
df = pd.read_csv(DATA_PATH)

# Ajout de la variable âge : Car_Age
current_year = datetime.now().year
df['Car_Age'] = current_year - df['Year']

# Stratification de 'Selling_Price' en 'Price_Category'
df['Price_Category'] = np.ceil(df['Selling_Price'] / 1.5)
df['Price_Category'] = df['Price_Category'].where(df['Price_Category'] < 5, 5.0)

# Standardisation de : Present_Price, Kms_Driven, Car_Age
scaler = StandardScaler()
df[['Present_Price_Std', 'Kms_Std', 'Car_Age_Std']] = scaler.fit_transform(df[['Present_Price', 'Kms_Driven', 'Car_Age']])

# Conversion des variables qualitatives en variables quantitatives
df["Fuel_Type_numeric"] = df["Fuel_Type"].map({"Petrol": 1, "Diesel": 2, "CNG": 3})
df["Seller_Type_numeric"] = df["Seller_Type"].map({"Dealer": 1, "Individual": 2})
df["Transmission_numeric"] = df["Transmission"].map({"Manual": 0, "Automatic": 1})

# Dataset standardisé pour entraînement
df_std = df[['Car_Age_Std', 'Selling_Price', 'Price_Category', 'Present_Price_Std', 'Kms_Std',
             "Fuel_Type_numeric", "Seller_Type_numeric", "Transmission_numeric"]]



# Features / Target
X = df_std.drop(['Selling_Price'], axis=1)
y = df_std['Selling_Price']

# STRATIFICATION
split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_index, test_index in split.split(df_std, df_std['Price_Category']):
    strat_train = df_std.loc[train_index]
    strat_test = df_std.loc[test_index]

# Division X / y
X_train = strat_train.drop(["Selling_Price", "Price_Category"], axis=1)
y_train = strat_train["Selling_Price"]

X_test = strat_test.drop(["Selling_Price", "Price_Category"], axis=1)
y_test = strat_test["Selling_Price"]

# Modèle linéaire
lin_reg = LinearRegression()
lin_reg.fit(X_train, y_train)

# Prédiction sur le set de test
y_pred = lin_reg.predict(X_test)


# ==== 1. Valeurs cibles de Martin (non standardisées) ====
martin_age = 7               # Âge maximum du véhicule
martin_kms = 100_000         # Kilométrage maximum
martin_transmission = 0      # 0 = boîte manuelle (voir mapping)

# ==== 2. Standardisation des valeurs de Martin ====
# Note : scaler a été entraîné sur ['Present_Price', 'Kms_Driven', 'Car_Age']
# On utilise 0 pour Present_Price juste pour respecter l’ordre
martin_df = pd.DataFrame([[0, martin_kms, martin_age]], columns=['Present_Price', 'Kms_Driven', 'Car_Age'])
present_price_std, kms_std, age_std = scaler.transform(martin_df)[0]

# ==== 3. Filtrage dans le DataFrame standardisé ====
df_martin = df_std[
    (df_std['Car_Age_Std'] <= age_std) &      # Âge max respecté
    (df_std['Kms_Std'] <= kms_std) &          # Kilométrage max respecté
    (df_std['Transmission_numeric'] == martin_transmission)  # Boîte manuelle
]

# ==== 4. Prédictions ====
# On retire la colonne cible et la catégorie pour obtenir les features
X_martin = df_martin.drop(['Selling_Price', 'Price_Category'], axis=1)

# Prédictions du modèle
y_martin_pred = lin_reg.predict(X_martin)

# Moyenne estimée
prix_moyen = np.mean(y_martin_pred)

# ==== 5. Résultat ====
print(f"Martin peut viser un prix autour de : {prix_moyen:.2f} milliers d'euros")

