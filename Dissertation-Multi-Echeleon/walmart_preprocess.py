import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================================
# 0) SET PATH (your folder)
# ==========================================================
DATA_DIR = Path("/Users/asus/Documents/Dissertation/WallmartData")
OUTPUT_DIR = DATA_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# ==========================================================
# 1) LOAD DATA
# ==========================================================
train_path = DATA_DIR / "train.csv"
features_path = DATA_DIR / "features.csv"
stores_path = DATA_DIR / "stores.csv"

# Safety check
for p in [train_path, features_path, stores_path]:
    if not p.exists():
        raise FileNotFoundError(f"❌ File not found: {p}")

train = pd.read_csv(train_path)
features = pd.read_csv(features_path)
stores = pd.read_csv(stores_path)

print("✅ Step 1: Data loaded")
print("Train:", train.shape, "| Features:", features.shape, "| Stores:", stores.shape)

# ==========================================================
# 2) CLEAN TYPES + PARSE DATES
# ==========================================================
train["Date"] = pd.to_datetime(train["Date"])
features["Date"] = pd.to_datetime(features["Date"])

train["Store"] = train["Store"].astype(int)
train["Dept"] = train["Dept"].astype(int)

features["Store"] = features["Store"].astype(int)
stores["Store"] = stores["Store"].astype(int)

# Ensure IsHoliday is boolean (sometimes read as object)
train["IsHoliday"] = train["IsHoliday"].astype(bool)
features["IsHoliday"] = features["IsHoliday"].astype(bool)

# Sort for time-series correctness
train = train.sort_values(["Store", "Dept", "Date"]).reset_index(drop=True)
features = features.sort_values(["Store", "Date"]).reset_index(drop=True)

print("✅ Step 2: Dates parsed + types cleaned")
print("Train date range:", train["Date"].min().date(), "to", train["Date"].max().date())

# ==========================================================
# 3) CHECK MISSING VALUES + DUPLICATES
# ==========================================================
print("\n✅ Step 3: Missing values check (Top 10 columns)")
missing_train = train.isna().mean().sort_values(ascending=False).head(10)
missing_features = features.isna().mean().sort_values(ascending=False).head(10)
missing_stores = stores.isna().mean().sort_values(ascending=False).head(10)

print("\nTrain missing (%):\n", (missing_train * 100).round(2))
print("\nFeatures missing (%):\n", (missing_features * 100).round(2))
print("\nStores missing (%):\n", (missing_stores * 100).round(2))

# Duplicates
dup_train = train.duplicated(subset=["Store", "Dept", "Date"]).sum()
dup_features = features.duplicated(subset=["Store", "Date"]).sum()
dup_stores = stores.duplicated(subset=["Store"]).sum()

print("\nDuplicates:")
print("Train duplicates (Store,Dept,Date):", dup_train)
print("Features duplicates (Store,Date):", dup_features)
print("Stores duplicates (Store):", dup_stores)

# ==========================================================
# 4) CLEAN FEATURES: HANDLE MISSING MARKDOWNS
# ==========================================================
# MarkDown columns are often missing. We'll fill with 0 because "no markdown info" usually means no markdown.
markdown_cols = ["MarkDown1", "MarkDown2", "MarkDown3", "MarkDown4", "MarkDown5"]
for col in markdown_cols:
    if col in features.columns:
        features[col] = features[col].fillna(0)

# Optional: also fill remaining missing numeric values with median
num_cols = features.select_dtypes(include=[np.number]).columns
for col in num_cols:
    if features[col].isna().any():
        features[col] = features[col].fillna(features[col].median())

print("✅ Step 4: Cleaned MarkDown columns + filled numeric missing values")

# ==========================================================
# 5) MERGE DATASETS (Train + Features + Stores)
# ==========================================================
# Merge train with features on Store+Date, then merge stores on Store
df = train.merge(features, on=["Store", "Date"], how="left", suffixes=("", "_feat"))
df = df.merge(stores, on="Store", how="left")

print("✅ Step 5: Merged dataset created")
print("Merged shape:", df.shape)

# Check if merge created missing (it shouldn't much)
merge_missing = df.isna().mean().sort_values(ascending=False).head(10)
print("\nTop missing columns after merge (%):\n", (merge_missing * 100).round(2))

# ==========================================================
# 6) BASIC DATA QUALITY FILTERS
# ==========================================================
# Some departments may have negative sales (returns/adjustments). Decide handling:
# For inventory demand simulation, negative demand is not meaningful, so we set negative sales to 0.
df["Weekly_Sales"] = df["Weekly_Sales"].clip(lower=0)

print("✅ Step 6: Negative Weekly_Sales handled (clipped to 0)")

# ==========================================================
# 7) CREATE DEMAND SERIES (Weekly demand time series)
# ==========================================================
# Option A: Create demand series for a specific Store & Dept (easy and clear)
TARGET_STORE = 1
TARGET_DEPT = 1

demand_series = (
    df[(df["Store"] == TARGET_STORE) & (df["Dept"] == TARGET_DEPT)]
    .sort_values("Date")[["Date", "Weekly_Sales", "IsHoliday", "Type", "Size"]]
    .reset_index(drop=True)
)

print("✅ Step 7: Demand series created for Store", TARGET_STORE, "Dept", TARGET_DEPT)
print("Demand series rows:", demand_series.shape[0])
print(demand_series.head())

# Option B (optional): Choose top 5 Store-Dept combinations by total sales
top_pairs = (
    df.groupby(["Store", "Dept"])["Weekly_Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

print("\nTop 5 Store-Dept pairs by total sales:\n", top_pairs)

# ==========================================================
# 8) SAVE OUTPUTS (for your dissertation submission)
# ==========================================================
df.to_csv(OUTPUT_DIR / "walmart_merged_clean.csv", index=False)
demand_series.to_csv(OUTPUT_DIR / f"demand_series_store{TARGET_STORE}_dept{TARGET_DEPT}.csv", index=False)
top_pairs.to_csv(OUTPUT_DIR / "top_5_store_dept_pairs.csv", index=False)

print("\n✅ Step 8: Files saved to:", OUTPUT_DIR)
print("Saved: walmart_merged_clean.csv")
print(f"Saved: demand_series_store{TARGET_STORE}_dept{TARGET_DEPT}.csv")
print("Saved: top_5_store_dept_pairs.csv")
