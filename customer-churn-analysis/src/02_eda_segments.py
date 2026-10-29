from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "processed" / "telco_churn_clean.csv")
OUT = ROOT / "outputs"

total_cust = len(df)
total_churn = int(df["ChurnFlag"].sum())
overall = total_churn / total_cust

lines = [f"Customers: {total_cust}", f"Churned customers: {total_churn}",
         f"Overall churn rate: {overall:.2%}"]

# Summary statistics
num = df[["tenure", "MonthlyCharges", "TotalCharges"]]
num.describe().round(2).to_csv(OUT / "summary_statistics.csv")
by = df.groupby("Churn")[["tenure", "MonthlyCharges", "TotalCharges"]].agg(["mean", "median"]).round(2)
by.to_csv(OUT / "numeric_by_churn.csv")
lines.append("\nMean/median by churn status:\n" + by.to_string())

# Revenue at risk: monthly recurring revenue lost to churners
mrr_lost = df.loc[df.ChurnFlag == 1, "MonthlyCharges"].sum()
mrr_total = df["MonthlyCharges"].sum()
lines.append(f"\nMonthly recurring revenue of churned customers: ${mrr_lost:,.0f} of ${mrr_total:,.0f} ({mrr_lost/mrr_total:.1%})")

dims = ["Contract", "PaymentMethod", "InternetService", "TenureGroup", "MonthlyChargesBand",
        "SeniorCitizen", "Partner", "Dependents", "PaperlessBilling", "OnlineSecurity",
        "TechSupport", "OnlineBackup", "DeviceProtection", "StreamingTV", "StreamingMovies",
        "MultipleLines", "PhoneService", "gender"]

def seg_table(col):
    g = df.groupby(col, observed=True).agg(customers=("ChurnFlag", "size"), churned=("ChurnFlag", "sum"))
    g["churn_rate_pct"] = (g.churned / g.customers * 100).round(2)
    g["share_of_customers_pct"] = (g.customers / total_cust * 100).round(2)
    g["share_of_all_churn_pct"] = (g.churned / total_churn * 100).round(2)
    g["lift_vs_overall"] = (g.churn_rate_pct / (overall * 100)).round(2)
    g.insert(0, "dimension", col)
    return g.reset_index().rename(columns={col: "segment"})

all_seg = pd.concat([seg_table(c) for c in dims], ignore_index=True)
for c in ["Contract", "PaymentMethod", "InternetService", "TenureGroup", "MonthlyChargesBand"]:
    seg_table(c).to_csv(OUT / f"churn_by_{c}.csv", index=False)

# Cross-segment: Contract x InternetService, Contract x TenureGroup, Internet x Payment
def cross(a, b):
    g = df.groupby([a, b], observed=True).agg(customers=("ChurnFlag", "size"), churned=("ChurnFlag", "sum")).reset_index()
    g["dimension"] = f"{a} x {b}"
    g["segment"] = g[a].astype(str) + " | " + g[b].astype(str)
    g["churn_rate_pct"] = (g.churned / g.customers * 100).round(2)
    g["share_of_customers_pct"] = (g.customers / total_cust * 100).round(2)
    g["share_of_all_churn_pct"] = (g.churned / total_churn * 100).round(2)
    g["lift_vs_overall"] = (g.churn_rate_pct / (overall * 100)).round(2)
    return g[all_seg.columns]

combo = pd.concat([cross("Contract", "InternetService"), cross("Contract", "TenureGroup"),
                   cross("InternetService", "PaymentMethod")], ignore_index=True)
combo = combo[combo.customers >= 100]  # ignore tiny segments
seg = pd.concat([all_seg, combo], ignore_index=True)
seg["rank_by_churn_rate"] = seg.groupby(seg.dimension.str.contains(" x "))["churn_rate_pct"].rank(ascending=False, method="min").astype(int)
seg["rank_by_churn_share"] = seg.groupby(seg.dimension.str.contains(" x "))["share_of_all_churn_pct"].rank(ascending=False, method="min").astype(int)
seg.sort_values("churn_rate_pct", ascending=False).to_csv(OUT / "segment_analysis.csv", index=False)

# Print headline views
cols = ["segment", "customers", "churned", "churn_rate_pct", "share_of_all_churn_pct"]
for c in ["Contract", "PaymentMethod", "InternetService", "TenureGroup", "MonthlyChargesBand"]:
    lines.append(f"\n{c}:\n" + seg_table(c)[cols].to_string(index=False))
lines.append("\nTop 10 combined segments by churn rate (n>=100):\n" +
             combo.sort_values("churn_rate_pct", ascending=False)[["segment", "customers", "churned", "churn_rate_pct", "share_of_all_churn_pct"]].head(10).to_string(index=False))
lines.append("\nTop 10 combined segments by share of all churn:\n" +
             combo.sort_values("share_of_all_churn_pct", ascending=False)[["segment", "customers", "churned", "churn_rate_pct", "share_of_all_churn_pct"]].head(10).to_string(index=False))
lines.append("\nAdd-on / demographic dims (churn rate):\n" + all_seg[all_seg.dimension.isin(["OnlineSecurity", "TechSupport", "SeniorCitizen", "PaperlessBilling", "Partner", "Dependents", "gender"])][["dimension"] + cols].to_string(index=False))

# Combined target: month-to-month + fiber + <=12 months
t = df[(df.Contract == "Month-to-month") & (df.InternetService == "Fiber optic") & (df.tenure <= 12)]
lines.append(f"\nM2M + Fiber + tenure<=12: n={len(t)}, churned={t.ChurnFlag.sum()}, rate={t.ChurnFlag.mean():.2%}, share of all churn={t.ChurnFlag.sum()/total_churn:.1%}")
t2 = df[(df.Contract == "Month-to-month") & (df.PaymentMethod == "Electronic check")]
lines.append(f"M2M + E-check: n={len(t2)}, churned={t2.ChurnFlag.sum()}, rate={t2.ChurnFlag.mean():.2%}, share of all churn={t2.ChurnFlag.sum()/total_churn:.1%}")
t3 = df[(df.Contract == "Month-to-month") & (df.TechSupport == "No") & (df.InternetService != "No")]
lines.append(f"M2M + Internet + no TechSupport: n={len(t3)}, rate={t3.ChurnFlag.mean():.2%}, share of all churn={t3.ChurnFlag.sum()/total_churn:.1%}")

(OUT / "key_metrics.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
