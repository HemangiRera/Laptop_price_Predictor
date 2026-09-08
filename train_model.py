import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

# -------------------------------------------------------------------
# 1. Load data
# -------------------------------------------------------------------
df = pd.read_csv("laptop_data.csv")
print("Dataset shape:", df.shape)
print("\nMissing values per column:\n", df.isnull().sum())

# -------------------------------------------------------------------
# 2. Basic EDA 
# -------------------------------------------------------------------
print("\n--- Price statistics ---")
print(df["Price"].describe())

print("\n--- Average price by Company ---")
print(df.groupby("Company")["Price"].mean().sort_values(ascending=False))

print("\n--- Correlation of numeric features with Price ---")
numeric_cols = ["Inches", "Ram", "Weight", "Touchscreen", "IPS", "PPI", "HDD", "SSD", "Price"]
print(df[numeric_cols].corr()["Price"].sort_values(ascending=False))

# -------------------------------------------------------------------
# 3. Split features / target
# -------------------------------------------------------------------
X = df.drop(columns=["Price", "Gpu_brand"])
y = df["Price"]

categorical_features = ["Company", "TypeName", "Cpu_brand", "Gpu_name", "OpSys"]
numeric_features = ["Inches", "Ram", "Weight", "Touchscreen", "IPS", "PPI", "HDD", "SSD"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------------------------------------------
# 4. Preprocessing + Model pipeline
# -------------------------------------------------------------------
preprocessor = ColumnTransformer(transformers=[
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
], remainder="passthrough") 

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", model)
])

# -------------------------------------------------------------------
# 5. Train
# -------------------------------------------------------------------
pipeline.fit(X_train, y_train)

# -------------------------------------------------------------------
# 6. Evaluate
# -------------------------------------------------------------------
y_pred = pipeline.predict(X_test)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print("\n--- Model Performance on Test Set ---")
print(f"R2 Score: {r2:.4f}   (closer to 1.0 is better)")
print(f"MAE     : Rs. {mae:,.0f}   (average prediction error in rupees)")

# -------------------------------------------------------------------
# 7. Feature importance
# -------------------------------------------------------------------
ohe = pipeline.named_steps["preprocessor"].named_transformers_["cat"]
ohe_feature_names = list(ohe.get_feature_names_out(categorical_features))
all_feature_names = ohe_feature_names + numeric_features
importances = pipeline.named_steps["regressor"].feature_importances_

feat_imp = pd.Series(importances, index=all_feature_names).sort_values(ascending=False)
print("\n--- Top 10 most important features ---")
print(feat_imp.head(10))

# -------------------------------------------------------------------
# 8. Save the trained pipeline 
# -------------------------------------------------------------------
with open("laptop_price_model.pkl", "wb") as f:
    pickle.dump(pipeline, f)
dropdown_values = {col: sorted(df[col].unique().tolist()) for col in categorical_features}
gpu_map = (
    df[["Gpu_brand", "Gpu_name"]]
    .drop_duplicates()
    .groupby("Gpu_brand")["Gpu_name"]
    .apply(lambda s: sorted(s.tolist()))
    .to_dict()
)
dropdown_values["Gpu_brand"] = sorted(gpu_map.keys())
dropdown_values["Gpu_map"] = gpu_map

with open("dropdown_values.pkl", "wb") as f:
    pickle.dump(dropdown_values, f)

print("\nSaved laptop_price_model.pkl and dropdown_values.pkl")
