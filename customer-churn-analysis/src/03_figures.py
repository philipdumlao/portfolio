from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
df = pd.read_csv(ROOT / "data" / "processed" / "telco_churn_clean.csv")
overall = df.ChurnFlag.mean() * 100
sns.set_theme(style="whitegrid", font_scale=1.0)
RETAINED, CHURNED = "#4C78A8", "#E45756"


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=150)
    plt.close(fig)


def rate_bar(col, title, name, order=None, rot=0):
    g = df.groupby(col, observed=True).ChurnFlag.agg(["mean", "size"]).mul([100, 1])
    g.columns = ["rate", "n"]
    g = g.loc[order] if order else g.sort_values("rate", ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(g.index.astype(str), g.rate, color=CHURNED)
    ax.axhline(overall, color="black", ls="--", lw=1, label=f"Overall churn {overall:.1f}%")
    for b, (r, n) in zip(bars, zip(g.rate, g.n)):
        ax.text(b.get_x() + b.get_width() / 2, r + 0.8, f"{r:.1f}%\n(n={int(n):,})", ha="center", fontsize=9)
    ax.set_ylabel("Churn rate (%)"); ax.set_ylim(0, g.rate.max() * 1.2)
    ax.set_title(title, fontweight="bold"); ax.legend()
    plt.setp(ax.get_xticklabels(), rotation=rot, ha="right" if rot else "center")
    save(fig, name)

#churn by contract / payment / internet
rate_bar("Contract", "Fig 1. Churn rate by contract type", "fig1_churn_by_contract.png",
         ["Month-to-month", "One year", "Two year"])
rate_bar("PaymentMethod", "Fig 2. Churn rate by payment method", "fig2_churn_by_payment_method.png", rot=15)
rate_bar("InternetService", "Fig 3. Churn rate by internet service", "fig3_churn_by_internet_service.png",
         ["Fiber optic", "DSL", "No"])

#tenure: churn rate by tenure group + tenure distribution
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
g = df.groupby("TenureGroup", observed=True).ChurnFlag.agg(["mean", "size"])
b = axes[0].bar(g.index.astype(str), g["mean"] * 100, color=CHURNED)
for r, (m, n) in zip(b, zip(g["mean"], g["size"])):
    axes[0].text(r.get_x() + r.get_width() / 2, m * 100 + 0.8, f"{m*100:.1f}%\n(n={n:,})", ha="center", fontsize=9)
axes[0].axhline(overall, color="black", ls="--", lw=1)
axes[0].set_ylim(0, 58); axes[0].set_ylabel("Churn rate (%)"); axes[0].set_title("Churn rate by tenure group")
sns.histplot(data=df, x="tenure", hue="Churn", bins=36, multiple="stack",
             palette={"No": RETAINED, "Yes": CHURNED}, ax=axes[1])
axes[1].set_xlabel("Tenure (months)"); axes[1].set_title("Customer count by tenure")
fig.suptitle("Fig 4. Churn and customer tenure", fontweight="bold")
save(fig, "fig4_churn_by_tenure.png")

#monthly charges
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
sns.kdeplot(data=df, x="MonthlyCharges", hue="Churn", fill=True, common_norm=False,
            palette={"No": RETAINED, "Yes": CHURNED}, ax=axes[0])
axes[0].set_title("Monthly charges distribution")
g = df.groupby("MonthlyChargesBand", observed=True).ChurnFlag.agg(["mean", "size"])
b = axes[1].bar(g.index.astype(str), g["mean"] * 100, color=CHURNED)
for r, (m, n) in zip(b, zip(g["mean"], g["size"])):
    axes[1].text(r.get_x() + r.get_width() / 2, m * 100 + 0.8, f"{m*100:.1f}%\n(n={n:,})", ha="center", fontsize=9)
axes[1].axhline(overall, color="black", ls="--", lw=1)
axes[1].set_ylim(0, 48); axes[1].set_ylabel("Churn rate (%)"); axes[1].set_title("Churn rate by monthly charge band")
fig.suptitle("Fig 5. Churn and monthly charges", fontweight="bold")
save(fig, "fig5_churn_by_monthly_charges.png")

#contract x tenure
order = ["0-12 months", "13-24 months", "25-48 months", "49-72 months"]
pv = df.pivot_table(index="Contract", columns="TenureGroup", values="ChurnFlag", aggfunc="mean", observed=True).mul(100)[order]
cnt = df.pivot_table(index="Contract", columns="TenureGroup", values="ChurnFlag", aggfunc="size", observed=True)[order]
pv = pv.loc[["Month-to-month", "One year", "Two year"]]; cnt = cnt.loc[pv.index]
annot = pv.round(1).astype(str) + "%\n(n=" + cnt.astype(str) + ")"
fig, ax = plt.subplots(figsize=(9, 4.8))
sns.heatmap(pv, annot=annot, fmt="", cmap="Reds", cbar_kws={"label": "Churn rate (%)"}, ax=ax, linewidths=.5)
ax.set_title("Fig 6. Churn rate: contract type x tenure group", fontweight="bold"); ax.set_xlabel(""); ax.set_ylabel("")
save(fig, "fig6_contract_vs_tenure.png")

#internet service x monthly charges
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
io = ["DSL", "Fiber optic", "No"]
sns.boxplot(data=df, x="InternetService", y="MonthlyCharges", hue="Churn", order=io,
            palette={"No": RETAINED, "Yes": CHURNED}, ax=axes[0])
axes[0].set_title("Monthly charges by internet service and churn")
pv2 = df.pivot_table(index="InternetService", columns="MonthlyChargesBand", values="ChurnFlag", aggfunc="mean", observed=True).mul(100).loc[io]
band_order = ["<=$35", "$35-70", "$70-90", ">$90"]
pv2 = pv2[band_order]
cn2 = df.pivot_table(index="InternetService", columns="MonthlyChargesBand", values="ChurnFlag", aggfunc="size", observed=True).loc[io][band_order]
an2 = pv2.round(1).astype(str).replace("nan", "") + "%\n(n=" + cn2.fillna(0).astype(int).astype(str) + ")"
an2 = an2.where(pv2.notna(), "")
sns.heatmap(pv2, annot=an2, fmt="", cmap="Reds", cbar_kws={"label": "Churn rate (%)"}, ax=axes[1], linewidths=.5)
axes[1].set_title("Churn rate: internet service x charge band"); axes[1].set_xlabel(""); axes[1].set_ylabel("")
fig.suptitle("Fig 7. Internet service vs monthly charges", fontweight="bold")
save(fig, "fig7_internet_vs_monthly_charges.png")

#(bonus) segment rate vs contribution
seg = pd.read_csv(ROOT / "outputs" / "segment_analysis.csv")
s = seg[seg.dimension.isin(["Contract", "PaymentMethod", "InternetService", "TenureGroup"])]
fig, ax = plt.subplots(figsize=(9, 6.5))
sc = ax.scatter(s.churn_rate_pct, s.share_of_all_churn_pct, s=s.customers / 6, alpha=.6, color=CHURNED, edgecolor="k")
for _, r in s.iterrows():
    ax.annotate({"InternetService": "Internet: ", "PaymentMethod": "", "Contract": "", "TenureGroup": ""}[r.dimension] + str(r.segment), (r.churn_rate_pct, r.share_of_all_churn_pct), fontsize=8, xytext=(5, 4), textcoords="offset points")
ax.axvline(overall, color="grey", ls="--", lw=1)
ax.set_xlabel("Churn rate within segment (%)"); ax.set_ylabel("Share of all churned customers (%)")
ax.set_title("Fig 8. Segment churn rate vs contribution to total churn\n(bubble size = customers; shares sum to 100% within each dimension)", fontweight="bold")
save(fig, "fig8_segment_rate_vs_contribution.png")
print("figures written:", sorted(p.name for p in FIG.glob("*.png")))
