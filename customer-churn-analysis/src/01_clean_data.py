
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
CLEAN = ROOT / "data" / "processed" / "telco_churn_clean.csv"
LOG = ROOT / "outputs" / "data_validation_report.txt"

lines = []


def log(msg=""):
    print(msg)
    lines.append(str(msg))


df = pd.read_csv(RAW)
log(f"Raw shape: {df.shape[0]} rows x {df.shape[1]} columns")

#Data types
log("\n[1] Data types (raw)")
log(df.dtypes.to_string())

#Missing values (NaN and blank strings hiding inside text columns)
blank = df.apply(lambda s: s.astype(str).str.strip().eq("").sum())
log("\n[2] Missing values")
nan_counts = df.isna().sum()
log("NaN per column: " + (nan_counts[nan_counts > 0].to_string() if nan_counts.sum() else "none"))
log("Blank-string values per column:\n" + (blank[blank > 0].to_string() if blank.sum() else "none"))

# TotalCharges is stored as text because of blank strings -> convert to numeric
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].astype(str).str.strip(), errors="coerce")
missing_tc = df[df["TotalCharges"].isna()]
log(f"\nTotalCharges blank/non-numeric rows: {len(missing_tc)}")
log(f"  tenure of those rows: {sorted(missing_tc['tenure'].unique())} (brand-new customers, not yet billed)")
# Business logic: tenure 0 -> nothing billed yet -> TotalCharges = 0
df.loc[df["TotalCharges"].isna() & (df["tenure"] == 0), "TotalCharges"] = 0.0
log(f"  Set to 0.0 because tenure = 0. Remaining NaN: {df['TotalCharges'].isna().sum()}")

#Duplicates
log("\n[3] Duplicates")
log(f"Duplicate rows: {df.duplicated().sum()}")
log(f"Duplicate customerIDs: {df['customerID'].duplicated().sum()}")

#Invalid values
log("\n[4] Invalid value checks")
log(f"tenure < 0: {(df['tenure'] < 0).sum()}")
log(f"MonthlyCharges <= 0: {(df['MonthlyCharges'] <= 0).sum()}")
log(f"TotalCharges < 0: {(df['TotalCharges'] < 0).sum()}")
log(f"SeniorCitizen not in {{0,1}}: {(~df['SeniorCitizen'].isin([0, 1])).sum()}")
log(f"Churn not in {{Yes,No}}: {(~df['Churn'].isin(['Yes', 'No'])).sum()}")
cat_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c]) and c != "customerID"]
log("Categorical value sets:")
for c in cat_cols:
    log(f"  {c}: {sorted(df[c].unique())}")

addons = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
no_net = df["InternetService"] == "No"
inconsistent = (no_net & (df[addons] != "No internet service").any(axis=1)).sum()
log(f"Internet add-on inconsistencies (InternetService = No): {inconsistent}")
nz = df[df["tenure"] > 0]
ratio = nz["TotalCharges"] / (nz["tenure"] * nz["MonthlyCharges"])
log(f"TotalCharges / (tenure x MonthlyCharges): median {ratio.median():.2f}, min {ratio.min():.2f}, max {ratio.max():.2f}")

#Derived columns
df["ChurnFlag"] = (df["Churn"] == "Yes").astype(int)
df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})
df["TenureGroup"] = pd.cut(df["tenure"], bins=[-1, 12, 24, 48, 72],
                           labels=["0-12 months", "13-24 months", "25-48 months", "49-72 months"])
df["MonthlyChargesBand"] = pd.cut(df["MonthlyCharges"], bins=[0, 35, 70, 90, 200],
                                  labels=["<=$35", "$35-70", "$70-90", ">$90"])
log("\n[5] Added columns: ChurnFlag, TenureGroup, MonthlyChargesBand; SeniorCitizen recoded 0/1 -> No/Yes")

df.to_csv(CLEAN, index=False)
log(f"\nSaved: {CLEAN.relative_to(ROOT)} ({df.shape[0]} rows x {df.shape[1]} cols)")
LOG.write_text("\n".join(lines), encoding="utf-8")
