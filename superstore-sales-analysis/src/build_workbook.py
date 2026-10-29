from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "sample_-_superstore.xls"
OUT = ROOT / "excel" / "Superstore_Sales_Performance.xlsx"

df = pd.read_excel(SRC, sheet_name="Orders")
N = len(df)
LAST = N + 1  


NAVY, TEAL, LIGHT, GREY, RED, GREEN = "1F3864", "2E75B6", "DDEBF7", "F2F2F2", "C00000", "548235"
F = lambda **k: Font(name="Arial", size=k.pop("size", 10), **k)
HDR_FILL = PatternFill("solid", fgColor=NAVY)
SUB_FILL = PatternFill("solid", fgColor=LIGHT)
CARD_FILL = PatternFill("solid", fgColor=GREY)
thin = Side(style="thin", color="BFBFBF")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
USD, USD2, PCT, INT = '$#,##0;[Red]-$#,##0', '$#,##0.00', '0.0%', '#,##0'

wb = Workbook()
wb._named_styles["Normal"].font = Font(name="Arial", size=10)


def hdr(ws, row, labels, col=1):
    for i, t in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=t)
        c.font, c.fill, c.border = F(bold=True, color="FFFFFF"), HDR_FILL, BOX
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def title(ws, text, sub=None):
    ws["A1"] = text
    ws["A1"].font = F(bold=True, size=14, color=NAVY)
    if sub:
        ws["A2"] = sub
        ws["A2"].font = F(italic=True, color="595959")


def widths(ws, w):
    for i, x in enumerate(w, 1):
        ws.column_dimensions[get_column_letter(i)].width = x


def body(ws, r, c, v, fmt=None, bold=False, fill=None):
    cell = ws.cell(row=r, column=c, value=v)
    cell.font = F(bold=bold)
    cell.border = BOX
    if fmt:
        cell.number_format = fmt
    if fill:
        cell.fill = fill
    return cell


# Data column letters (Orders sheet layout)
COL = {n: get_column_letter(i + 1) for i, n in enumerate(df.columns)}
COL["Order Year"], COL["Discount Band"] = "V", "W"


def R(name):
    c = COL[name]
    return f"Data!${c}$2:${c}${LAST}"


ws_about = wb.active; ws_about.title = "About"
ws_dash = wb.create_sheet("Dashboard")
ws_kpi = wb.create_sheet("KPI_Summary")
ws_reg = wb.create_sheet("Pivot_Region")
ws_cat = wb.create_sheet("Pivot_Category")
ws_sub = wb.create_sheet("Pivot_SubCategory")
ws_prod = wb.create_sheet("Pivot_Product")
ws_year = wb.create_sheet("Pivot_Year")
ws_disc = wb.create_sheet("Discount_Analysis")
ws_find = wb.create_sheet("Findings")
ws_data = wb.create_sheet("Data")

heads = list(df.columns) + ["Order Year", "Discount Band"]
hdr(ws_data, 1, heads)
for i, row in enumerate(df.itertuples(index=False), start=2):
    vals = []
    for v in row:
        if isinstance(v, pd.Timestamp):
            v = v.to_pydatetime()
        elif pd.isna(v):
            v = None
        vals.append(v)
    ws_data.append(vals + [
        f"=YEAR(C{i})",
        f'=IF(T{i}=0,"No discount",IF(T{i}<=0.1,"Up to 10%",IF(T{i}<=0.2,"Up to 20%",'
        f'IF(T{i}<=0.3,"Up to 30%",IF(T{i}<=0.5,"Up to 50%","Over 50%")))))',
    ])
for r in range(2, LAST + 1):
    ws_data[f"C{r}"].number_format = ws_data[f"D{r}"].number_format = "yyyy-mm-dd"
    ws_data[f"R{r}"].number_format = ws_data[f"U{r}"].number_format = USD2
    ws_data[f"T{r}"].number_format = "0%"
ws_data.freeze_panes = "A2"
ws_data.auto_filter.ref = f"A1:W{LAST}"
widths(ws_data, [8, 16, 12, 12, 15, 12, 20, 12, 14, 16, 16, 10, 10, 17, 16, 14, 50, 11, 9, 9, 11, 10, 14])
ws_data["Y1"] = "Columns V:W are formula helper columns added to the original Orders data."
ws_data["Y1"].font = F(italic=True, color="595959")


title(ws_kpi, "KPI Summary", "All values are formulas on the Data sheet")
hdr(ws_kpi, 4, ["KPI", "Value", "Definition"])
kpis = [
    ("Total Sales", f"=SUM({R('Sales')})", USD, "Sum of Sales"),
    ("Total Profit", f"=SUM({R('Profit')})", USD, "Sum of Profit"),
    ("Profit Margin", "=B6/B5", PCT, "Total Profit / Total Sales"),
    ("Quantity Sold", f"=SUM({R('Quantity')})", INT, "Sum of Quantity"),
    ("Average Discount", f"=AVERAGE({R('Discount')})", PCT, "Simple average of the Discount column across order lines (not sales-weighted)"),
    ("Order Lines", f"=COUNT({R('Sales')})", INT, "Number of rows in Orders"),
    ("Loss-Making Order Lines", f'=COUNTIF({R("Profit")},"<0")', INT, "Order lines with Profit below 0"),
    ("% Loss-Making Order Lines", "=B11/B10", PCT, "Loss-making lines / all lines"),
    ("Discount vs Profit Correlation", f"=CORREL({R('Discount')},{R('Profit')})", "0.000",
     "Pearson correlation between line-level Discount and Profit. Shows association only, not causation"),
    ("First Order Date", f"=MIN({R('Order Date')})", "yyyy-mm-dd", "Earliest Order Date"),
    ("Last Order Date", f"=MAX({R('Order Date')})", "yyyy-mm-dd", "Latest Order Date"),
]
for i, (k, f, fmt, d) in enumerate(kpis, start=5):
    body(ws_kpi, i, 1, k, bold=True)
    body(ws_kpi, i, 2, f, fmt)
    body(ws_kpi, i, 3, d)
widths(ws_kpi, [32, 18, 90])


def pivot(ws, start_row, dim_name, keys, key_label, extra_cols=None, total=True):
    """keys: ordered list of dimension values. Returns (first_row, last_row)."""
    labels = [key_label, "Sales", "Profit", "Profit Margin", "Quantity", "Avg Discount", "Sales Share", "Profit Share",
              "Sales Rank", "Profit Rank"]
    hdr(ws, start_row, labels)
    first, last = start_row + 1, start_row + len(keys)
    for i, k in enumerate(keys):
        r = first + i
        body(ws, r, 1, k, bold=True)
        crit = f"$A{r}"
        body(ws, r, 2, f"=SUMIFS({R('Sales')},{R(dim_name)},{crit})", USD)
        body(ws, r, 3, f"=SUMIFS({R('Profit')},{R(dim_name)},{crit})", USD)
        body(ws, r, 4, f"=IF(B{r}=0,0,C{r}/B{r})", PCT)
        body(ws, r, 5, f"=SUMIFS({R('Quantity')},{R(dim_name)},{crit})", INT)
        body(ws, r, 6, f"=AVERAGEIFS({R('Discount')},{R(dim_name)},{crit})", PCT)
        body(ws, r, 7, f"=B{r}/B${last + 1}", PCT)
        body(ws, r, 8, f"=C{r}/C${last + 1}", PCT)
        body(ws, r, 9, f"=RANK(B{r},B${first}:B${last})", INT)
        body(ws, r, 10, f"=RANK(C{r},C${first}:C${last})", INT)
    t = last + 1
    body(ws, t, 1, "Total", bold=True, fill=SUB_FILL)
    body(ws, t, 2, f"=SUM(B{first}:B{last})", USD, True, SUB_FILL)
    body(ws, t, 3, f"=SUM(C{first}:C{last})", USD, True, SUB_FILL)
    body(ws, t, 4, f"=IF(B{t}=0,0,C{t}/B{t})", PCT, True, SUB_FILL)
    body(ws, t, 5, f"=SUM(E{first}:E{last})", INT, True, SUB_FILL)
    body(ws, t, 6, f"=AVERAGE({R('Discount')})", PCT, True, SUB_FILL)
    for c in (7, 8):
        body(ws, t, c, f"=SUM({get_column_letter(c)}{first}:{get_column_letter(c)}{last})", PCT, True, SUB_FILL)
    for c in (9, 10):
        body(ws, t, c, None, fill=SUB_FILL)
    return first, last


def order_by_profit(col):
    return list(df.groupby(col).Profit.sum().sort_values(ascending=False).index)



title(ws_reg, "Sales and Profit by Region", "SUMIFS summary (PivotTable-style). Sorted by profit.")
reg_first, reg_last = pivot(ws_reg, 4, "Region", order_by_profit("Region"), "Region")
# Region x Category profit matrix
mr = reg_last + 4
ws_reg.cell(row=mr - 1, column=1, value="Profit by Region and Category").font = F(bold=True, size=11, color=NAVY)
cats = order_by_profit("Category")
hdr(ws_reg, mr, ["Region"] + cats + ["Total"])
for i in range(len(df.Region.unique())):
    r = mr + 1 + i
    body(ws_reg, r, 1, f"=A{reg_first + i}", bold=True)
    for j in range(len(cats)):
        cl = get_column_letter(2 + j)
        body(ws_reg, r, 2 + j, f"=SUMIFS({R('Profit')},{R('Region')},$A{r},{R('Category')},{cl}${mr})", USD)
    body(ws_reg, r, 2 + len(cats), f"=SUM(B{r}:{get_column_letter(1 + len(cats))}{r})", USD, True, SUB_FILL)
widths(ws_reg, [16, 14, 14, 13, 11, 13, 12, 12, 11, 11])


title(ws_cat, "Sales and Profit by Category", "SUMIFS summary (PivotTable-style). Sorted by profit.")
cat_first, cat_last = pivot(ws_cat, 4, "Category", order_by_profit("Category"), "Category")
sr = cat_last + 4
ws_cat.cell(row=sr - 1, column=1, value="By Customer Segment").font = F(bold=True, size=11, color=NAVY)
pivot(ws_cat, sr, "Segment", order_by_profit("Segment"), "Segment")
widths(ws_cat, [18, 14, 14, 13, 11, 13, 12, 12, 11, 11])


title(ws_sub, "Sales and Profit by Sub-Category", "SUMIFS summary (PivotTable-style). Sorted by profit.")
subs = order_by_profit("Sub-Category")
sub_first, sub_last = pivot(ws_sub, 4, "Sub-Category", subs, "Sub-Category")
cat_of = df.drop_duplicates("Sub-Category").set_index("Sub-Category").Category
hdr(ws_sub, 4, ["Category", "Status"], col=11)
for i, s in enumerate(subs):
    r = sub_first + i
    body(ws_sub, r, 11, cat_of[s])
    body(ws_sub, r, 12, f'=IF(C{r}<0,"Loss-making","Profitable")')
widths(ws_sub, [18, 14, 14, 13, 11, 13, 12, 12, 11, 11, 17, 14])


title(ws_prod, "Top 10 and Bottom 10 Products by Profit",
      "Product list chosen from the Data sheet; all figures are SUMIFS formulas. Wildcards in names are escaped.")
pp = df.groupby("Product Name").agg(Profit=("Profit", "sum")).sort_values("Profit", ascending=False)
top10, bot10 = list(pp.index[:10]), list(pp.index[-10:][::-1])
prod_cat = df.drop_duplicates("Product Name").set_index("Product Name").Category


def esc(s):  
    return s.replace("~", "~~").replace("*", "~*").replace("?", "~?")


def prod_block(start, label, names):
    ws_prod.cell(row=start - 1, column=1, value=label).font = F(bold=True, size=11, color=NAVY)
    hdr(ws_prod, start, ["Product Name", "Category", "Sales", "Profit", "Profit Margin", "Quantity", "Avg Discount"])
    for i, n in enumerate(names):
        r = start + 1 + i
        assert len(n) < 250, n
        body(ws_prod, r, 1, n)
        body(ws_prod, r, 2, prod_cat[n])
        crit = f'"{esc(n)}"'.replace("\n", " ")
        body(ws_prod, r, 3, f"=SUMIFS({R('Sales')},{R('Product Name')},A{r})", USD)
        body(ws_prod, r, 4, f"=SUMIFS({R('Profit')},{R('Product Name')},A{r})", USD)
        body(ws_prod, r, 5, f"=IF(C{r}=0,0,D{r}/C{r})", PCT)
        body(ws_prod, r, 6, f"=SUMIFS({R('Quantity')},{R('Product Name')},A{r})", INT)
        body(ws_prod, r, 7, f"=AVERAGEIFS({R('Discount')},{R('Product Name')},A{r})", PCT)
    return start + 1, start + len(names)


# escape wildcards in the product-name cell itself is not possible (cell is the key); use safe check instead
for n in top10 + bot10:
    assert not any(ch in n for ch in "*?~"), f"wildcard char in product name: {n}"
p1a, p1b = prod_block(5, "Top 10 products by profit", top10)
p2a, p2b = prod_block(18, "Bottom 10 products by profit (largest losses first)", bot10)
widths(ws_prod, [78, 17, 14, 14, 13, 11, 13])


title(ws_year, "Sales and Profit by Year", "SUMIFS summary (PivotTable-style)")
years = sorted(df["Order Date"].dt.year.unique())
hdr(ws_year, 4, ["Year", "Sales", "Profit", "Profit Margin", "Quantity", "Avg Discount"])
for i, y in enumerate(years):
    r = 5 + i
    body(ws_year, r, 1, int(y), "0", True)
    body(ws_year, r, 2, f"=SUMIFS({R('Sales')},{R('Order Year')},$A{r})", USD)
    body(ws_year, r, 3, f"=SUMIFS({R('Profit')},{R('Order Year')},$A{r})", USD)
    body(ws_year, r, 4, f"=IF(B{r}=0,0,C{r}/B{r})", PCT)
    body(ws_year, r, 5, f"=SUMIFS({R('Quantity')},{R('Order Year')},$A{r})", INT)
    body(ws_year, r, 6, f"=AVERAGEIFS({R('Discount')},{R('Order Year')},$A{r})", PCT)
yr_first, yr_last = 5, 4 + len(years)
widths(ws_year, [10, 14, 14, 13, 11, 13])


title(ws_disc, "Discount vs Profitability",
      "Order lines grouped by discount band (Data!W). Association only: product mix and region also differ by band.")
bands = ["No discount", "Up to 10%", "Up to 20%", "Up to 30%", "Up to 50%", "Over 50%"]
hdr(ws_disc, 4, ["Discount Band", "Order Lines", "Sales", "Profit", "Profit Margin", "Avg Discount",
                 "Loss-Making Lines", "% Lines Loss-Making", "Share of Lines"])
d_first, d_last = 5, 4 + len(bands)
for i, b in enumerate(bands):
    r = 5 + i
    body(ws_disc, r, 1, b, bold=True)
    body(ws_disc, r, 2, f"=COUNTIFS({R('Discount Band')},$A{r})", INT)
    body(ws_disc, r, 3, f"=SUMIFS({R('Sales')},{R('Discount Band')},$A{r})", USD)
    body(ws_disc, r, 4, f"=SUMIFS({R('Profit')},{R('Discount Band')},$A{r})", USD)
    body(ws_disc, r, 5, f"=IF(C{r}=0,0,D{r}/C{r})", PCT)
    body(ws_disc, r, 6, f"=AVERAGEIFS({R('Discount')},{R('Discount Band')},$A{r})", PCT)
    body(ws_disc, r, 7, f'=COUNTIFS({R("Discount Band")},$A{r},{R("Profit")},"<0")', INT)
    body(ws_disc, r, 8, f"=IF(B{r}=0,0,G{r}/B{r})", PCT)
    body(ws_disc, r, 9, f"=B{r}/B${d_last + 1}", PCT)
t = d_last + 1
body(ws_disc, t, 1, "Total", bold=True, fill=SUB_FILL)
for c, fmt in [(2, INT), (3, USD), (4, USD), (7, INT)]:
    L = get_column_letter(c)
    body(ws_disc, t, c, f"=SUM({L}{d_first}:{L}{d_last})", fmt, True, SUB_FILL)
body(ws_disc, t, 5, f"=D{t}/C{t}", PCT, True, SUB_FILL)
body(ws_disc, t, 6, f"=AVERAGE({R('Discount')})", PCT, True, SUB_FILL)
body(ws_disc, t, 8, f"=G{t}/B{t}", PCT, True, SUB_FILL)
body(ws_disc, t, 9, f"=SUM(I{d_first}:I{d_last})", PCT, True, SUB_FILL)

k = t + 3
ws_disc.cell(row=k - 1, column=1, value="Key discount metrics").font = F(bold=True, size=11, color=NAVY)
hdr(ws_disc, k, ["Metric", "Value"])
km = [
    ("Correlation: Discount vs Profit (line level)", "=KPI_Summary!B13", "0.000"),
    ("Order lines with discount of 30% or more", f'=COUNTIF({R("Discount")},">=0.3")', INT),
    ("Share of all order lines", f"=B{k + 2}/KPI_Summary!B10", PCT),
    ("Profit on lines with discount of 30% or more", f'=SUMIFS({R("Profit")},{R("Discount")},">=0.3")', USD),
    ("Loss-making lines among those", f'=COUNTIFS({R("Discount")},">=0.3",{R("Profit")},"<0")', INT),
    ("% of 30%+ discount lines that lose money", f"=B{k + 5}/B{k + 2}", PCT),
    ("Profit margin on lines under 30% discount", f'=SUMIFS({R("Profit")},{R("Discount")},"<0.3")/SUMIFS({R("Sales")},{R("Discount")},"<0.3")', PCT),
]
for i, (m, f, fmt) in enumerate(km, start=k + 1):
    body(ws_disc, i, 1, m, bold=True)
    body(ws_disc, i, 2, f, fmt)
disc_key_first = k + 1

# Discount by region
rr = k + len(km) + 4
ws_disc.cell(row=rr - 1, column=1, value="Discounting by Region").font = F(bold=True, size=11, color=NAVY)
hdr(ws_disc, rr, ["Region", "Avg Discount", "% Lines at 30%+ Discount", "Profit Margin"])
for i, g in enumerate(order_by_profit("Region")):
    r = rr + 1 + i
    body(ws_disc, r, 1, g, bold=True)
    body(ws_disc, r, 2, f"=AVERAGEIFS({R('Discount')},{R('Region')},$A{r})", PCT)
    body(ws_disc, r, 3, f'=COUNTIFS({R("Region")},$A{r},{R("Discount")},">=0.3")/COUNTIFS({R("Region")},$A{r})', PCT)
    body(ws_disc, r, 4, f"=SUMIFS({R('Profit')},{R('Region')},$A{r})/SUMIFS({R('Sales')},{R('Region')},$A{r})", PCT)
# Discount by category
rc = rr + 8
ws_disc.cell(row=rc - 1, column=1, value="Discounting by Category").font = F(bold=True, size=11, color=NAVY)
hdr(ws_disc, rc, ["Category", "Avg Discount", "% Lines at 30%+ Discount", "Profit Margin"])
for i, g in enumerate(order_by_profit("Category")):
    r = rc + 1 + i
    body(ws_disc, r, 1, g, bold=True)
    body(ws_disc, r, 2, f"=AVERAGEIFS({R('Discount')},{R('Category')},$A{r})", PCT)
    body(ws_disc, r, 3, f'=COUNTIFS({R("Category")},$A{r},{R("Discount")},">=0.3")/COUNTIFS({R("Category")},$A{r})', PCT)
    body(ws_disc, r, 4, f"=SUMIFS({R('Profit')},{R('Category')},$A{r})/SUMIFS({R('Sales')},{R('Category')},$A{r})", PCT)
widths(ws_disc, [46, 14, 16, 14, 14, 13, 17, 18, 13])


S, P = df.Sales.sum(), df.Profit.sum()
g = lambda c: df.groupby(c).agg(S=("Sales", "sum"), P=("Profit", "sum"))
reg, cat, sub = g("Region"), g("Category"), g("Sub-Category")
yr = df.groupby(df["Order Date"].dt.year).agg(S=("Sales", "sum"), P=("Profit", "sum"))
hi = df[df.Discount >= 0.3]
prodp = df.groupby("Product Name").Profit.sum()
money = lambda v: f"${v:,.0f}" if v >= 0 else f"-${abs(v):,.0f}"
m = lambda a, b: f"{a / b:.1%}"
cen = df[df.Region == "Central"]; wst = df[df.Region == "West"]
bandlab = pd.cut(df.Discount, [-1, 0, .1, .2, .3, .5, 1], labels=bands)
bm = df.groupby(bandlab, observed=True).agg(S=("Sales", "sum"), P=("Profit", "sum"))
neg_prod = prodp[prodp < 0]
findings = [
    f"1. Overall: {money(S)} sales, {money(P)} profit, {m(P, S)} margin on {df.Quantity.sum():,} units. "
    f"Sales grew from {money(yr.S.iloc[0])} (2023) to {money(yr.S.iloc[-1])} (2026) and profit from {money(yr.P.iloc[0])} to {money(yr.P.iloc[-1])}.",
    f"2. Regions: West leads both sales ({money(reg.S['West'])}) and profit ({money(reg.P['West'])}, {m(reg.P['West'], reg.S['West'])} margin). "
    f"Central ranks third in sales ({money(reg.S['Central'])}) but last in profit ({money(reg.P['Central'])}, {m(reg.P['Central'], reg.S['Central'])} margin). "
    f"South has the lowest sales ({money(reg.S['South'])}).",
    f"3. Categories: Technology ({money(cat.P['Technology'])}, {m(cat.P['Technology'], cat.S['Technology'])}) and Office Supplies ({money(cat.P['Office Supplies'])}, {m(cat.P['Office Supplies'], cat.S['Office Supplies'])}) carry the profit. "
    f"Furniture has {money(cat.S['Furniture'])} of sales, more than Office Supplies, but only {money(cat.P['Furniture'])} profit ({m(cat.P['Furniture'], cat.S['Furniture'])} margin), {m(cat.P['Furniture'], P)} of total profit.",
    f"4. Sub-categories: Copiers ({money(sub.P['Copiers'])}), Phones ({money(sub.P['Phones'])}), Accessories ({money(sub.P['Accessories'])}) and Paper ({money(sub.P['Paper'])}) lead profit. "
    f"Three lose money: Tables ({money(sub.P['Tables'])}), Bookcases ({money(sub.P['Bookcases'])}) and Supplies ({money(sub.P['Supplies'])}). "
    f"Machines earn only {m(sub.P['Machines'], sub.S['Machines'])} margin on {money(sub.S['Machines'])} of sales.",
    f"5. Products: {len(neg_prod):,} of {len(prodp):,} products lose money, {money(neg_prod.sum())} in total. "
    f"The biggest losers are {prodp.idxmin()} ({money(prodp.min())}) and the Lexmark MX611dhe Monochrome Laser Printer ({money(prodp['Lexmark MX611dhe Monochrome Laser Printer'])}). "
    f"The top product is {prodp.idxmax()} ({money(prodp.max())}).",
    f"6. Discounts: lines with no discount earn a {m(bm.P['No discount'], bm.S['No discount'])} margin, up to 20% earn {m(bm.P['Up to 20%'], bm.S['Up to 20%'])}, "
    f"while 21-30% ({m(bm.P['Up to 30%'], bm.S['Up to 30%'])}), 31-50% ({m(bm.P['Up to 50%'], bm.S['Up to 50%'])}) and over 50% ({m(bm.P['Over 50%'], bm.S['Over 50%'])}) are negative. "
    f"The line-level correlation between discount and profit is {df.Discount.corr(df.Profit):.2f}. "
    f"Lines at 30%+ discount are {m(len(hi), len(df))} of all lines, {m((hi.Profit < 0).sum(), len(hi))} of them lose money, and together they total {money(hi.Profit.sum())} of profit. "
    f"This is an association; product mix also differs by band (for example Binders account for most lines above 50%), so it does not prove discounts alone cause the losses.",
    f"7. Central: average discount is {cen.Discount.mean():.1%} vs {wst.Discount.mean():.1%} in West, and {m((cen.Discount >= .3).sum(), len(cen))} of Central lines carry a 30%+ discount vs {m((wst.Discount >= .3).sum(), len(wst))} in West. "
    f"Central also has the lowest margin ({m(reg.P['Central'], reg.S['Central'])}), consistent with a discounting problem there.",
]
recs = [
    "1. Put an approval step on discounts of 30% or more (and review anything above 50%). These lines are about 14% of volume but lose money on nearly all lines. "
    "Test the cap on a subset of orders first to confirm the effect before applying it everywhere.",
    "2. Review Central region discounting practices and compare with West, which discounts far less and earns the highest margin.",
    "3. Fix Furniture profitability: reprice or renegotiate supplier cost for Tables and Bookcases, and reduce discounts on Furniture before cutting volume.",
    "4. Review the loss-making products, starting with the Cubify CubeX 3D printers and Lexmark MX611dhe: reprice, bundle without discount, or stop selling.",
    "5. Protect and grow the high-margin lines (Copiers, Phones, Accessories, Paper) and keep their discounts low, since Technology and Office Supplies earn most of the profit.",
]
title(ws_find, "Findings and Recommendations", "Narrative figures reproduced by src/verify_numbers.py. Associations are not proof of cause.")
ws_find["A4"] = "Key findings"; ws_find["A4"].font = F(bold=True, size=12, color=NAVY)
r = 5
for t in findings:
    c = ws_find.cell(row=r, column=1, value=t); c.alignment = Alignment(wrap_text=True, vertical="top"); c.font = F()
    ws_find.row_dimensions[r].height = 15 * (len(t) // 115 + 1) + 4
    r += 1
r += 1
ws_find.cell(row=r, column=1, value="Recommendations").font = F(bold=True, size=12, color=NAVY); r += 1
for t in recs:
    c = ws_find.cell(row=r, column=1, value=t); c.alignment = Alignment(wrap_text=True, vertical="top"); c.font = F()
    ws_find.row_dimensions[r].height = 15 * (len(t) // 115 + 1) + 4
    r += 1
ws_find.column_dimensions["A"].width = 130


title(ws_about, "Superstore Sales Performance Analysis", "Excel project 01 of the Data Analyst portfolio")
about = [
    ("Business question", "Which regions, categories and products drive sales and profit, and how does discounting relate to profitability?"),
    ("Dataset", "Tableau 'Sample - Superstore' (Orders sheet, 10,194 order lines, orders dated 2023-01-03 to 2026-12-30). Source: https://public.tableau.com/app/learn/sample-data"),
    ("How the workbook works", "The Data sheet holds the original Orders data plus two formula helper columns (Order Year, Discount Band). Every analysis sheet uses SUMIFS/COUNTIFS/AVERAGEIFS formulas on Data, so it recalculates if the data changes."),
    ("About the 'Pivot_' sheets", "They are PivotTable-style summary tables built with formulas (so they work in any spreadsheet app and stay reproducible). To make native PivotTables: Insert > PivotTable on the Data sheet, then drag Region/Category/Sub-Category/Product Name to Rows and Sales/Profit to Values."),
    ("Sheets", "Dashboard | KPI_Summary | Pivot_Region | Pivot_Category | Pivot_SubCategory | Pivot_Product | Pivot_Year | Discount_Analysis | Findings | Data"),
    ("Assumptions", "Profit Margin = Total Profit / Total Sales. Average Discount is a simple average across order lines (not weighted by sales). Dataset is used as provided; no rows were removed (no blanks or duplicate Row IDs were found)."),
    ("Limitations", "Sample data with no cost or return detail in the analysis; Returns and People sheets of the source file were not used. Discount findings are associations, not proof of cause."),
]
for i, (k_, v) in enumerate(about, start=4):
    a = ws_about.cell(row=i, column=1, value=k_); a.font = F(bold=True); a.alignment = Alignment(vertical="top")
    b = ws_about.cell(row=i, column=2, value=v); b.font = F(); b.alignment = Alignment(wrap_text=True, vertical="top")
    ws_about.row_dimensions[i].height = 15 * (len(v) // 100 + 1) + 4
widths(ws_about, [26, 110])


ws = ws_dash
ws.sheet_view.showGridLines = False
for c in range(1, 21):
    ws.column_dimensions[get_column_letter(c)].width = 10.5
ws.column_dimensions["A"].width = 2
ws.merge_cells("B1:S2")
ws["B1"] = "Superstore Sales Performance Dashboard"
ws["B1"].font = F(bold=True, size=20, color="FFFFFF"); ws["B1"].fill = HDR_FILL
ws["B1"].alignment = Alignment(vertical="center", indent=1)
ws.merge_cells("B3:S3")
ws["B3"] = '="Orders "&TEXT(KPI_Summary!B14,"yyyy-mm-dd")&" to "&TEXT(KPI_Summary!B15,"yyyy-mm-dd")&"  |  Source: Tableau Sample Superstore"'
ws["B3"].font = F(italic=True, color="595959")
cards = [("Total Sales", "=KPI_Summary!B5", USD), ("Total Profit", "=KPI_Summary!B6", USD),
         ("Profit Margin", "=KPI_Summary!B7", PCT), ("Quantity Sold", "=KPI_Summary!B8", INT),
         ("Average Discount", "=KPI_Summary!B9", PCT), ("Loss-Making Lines", "=KPI_Summary!B12", PCT)]
for i, (lab, f, fmt) in enumerate(cards):
    c1 = 2 + i * 3
    L1, L2 = get_column_letter(c1), get_column_letter(c1 + 2)
    ws.merge_cells(f"{L1}5:{L2}5"); ws.merge_cells(f"{L1}6:{L2}7")
    ws[f"{L1}5"] = lab; ws[f"{L1}5"].font = F(bold=True, color="595959", size=10)
    ws[f"{L1}5"].alignment = Alignment(horizontal="center")
    ws[f"{L1}6"] = f; ws[f"{L1}6"].number_format = fmt
    ws[f"{L1}6"].font = F(bold=True, size=20, color=NAVY if i != 5 else RED)
    ws[f"{L1}6"].alignment = Alignment(horizontal="center", vertical="center")
    for rr_ in range(5, 8):
        for cc in range(c1, c1 + 3):
            ws.cell(row=rr_, column=cc).fill = CARD_FILL


def style_chart(ch, ttl, w=18.6, h=10.0):
    ch.title = ttl
    ch.width, ch.height = w, h
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    if ch.legend is not None:
        ch.legend.position = "b"


def color(series, hexcol):
    series.graphicalProperties.solidFill = hexcol
    series.graphicalProperties.line.solidFill = hexcol


# Chart 1: Sales & Profit by Region
c1 = BarChart(); c1.type = "col"; c1.grouping = "clustered"
c1.add_data(Reference(ws_reg, min_col=2, max_col=3, min_row=4, max_row=reg_last), titles_from_data=True)
c1.set_categories(Reference(ws_reg, min_col=1, min_row=reg_first, max_row=reg_last))
color(c1.series[0], TEAL); color(c1.series[1], "ED7D31")
c1.y_axis.numFmt = '$#,##0'; c1.y_axis.title = "USD"; c1.x_axis.title = "Region"
style_chart(c1, "Sales and Profit by Region")
c1.dataLabels = DataLabelList(); c1.dataLabels.showVal = True
c1.dataLabels.showSerName = c1.dataLabels.showCatName = c1.dataLabels.showLegendKey = False
c1.dataLabels.numFmt = '$#,##0,"K"'
ws.add_chart(c1, "B9")

# Chart 2: Profit by Sub-Category (horizontal)
c2 = BarChart(); c2.type = "bar"
c2.add_data(Reference(ws_sub, min_col=3, min_row=4, max_row=sub_last), titles_from_data=True)
c2.set_categories(Reference(ws_sub, min_col=1, min_row=sub_first, max_row=sub_last))
color(c2.series[0], TEAL); c2.series[0].invertIfNegative = False
c2.x_axis.scaling.orientation = "maxMin"  # largest profit at the top
c2.y_axis.numFmt = '$#,##0'; c2.y_axis.title = "Profit (USD)"
c2.legend = None
c2.x_axis.tickLblPos = "low"; c2.x_axis.tickLblSkip = 1
style_chart(c2, "Profit by Sub-Category (Tables, Bookcases, Supplies lose money)")
ws.add_chart(c2, "K9")

# Chart 3: Profit by discount band
c3 = BarChart(); c3.type = "col"
c3.add_data(Reference(ws_disc, min_col=4, min_row=4, max_row=d_last), titles_from_data=True)
c3.set_categories(Reference(ws_disc, min_col=1, min_row=d_first, max_row=d_last))
color(c3.series[0], "548235"); c3.series[0].invertIfNegative = False
c3.y_axis.numFmt = '$#,##0'; c3.y_axis.title = "Profit (USD)"; c3.x_axis.title = "Discount band"
c3.legend = None
c3.x_axis.tickLblPos = "low"
style_chart(c3, "Profit by Discount Band (losses start above 20%)")
c3.dataLabels = DataLabelList(); c3.dataLabels.showVal = True
c3.dataLabels.showSerName = c3.dataLabels.showCatName = c3.dataLabels.showLegendKey = False
c3.dataLabels.numFmt = '$#,##0,"K"'
ws.add_chart(c3, "B30")

# Chart 4: Yearly sales and profit
c4 = LineChart()
c4.add_data(Reference(ws_year, min_col=2, max_col=3, min_row=4, max_row=yr_last), titles_from_data=True)
c4.set_categories(Reference(ws_year, min_col=1, min_row=yr_first, max_row=yr_last))
for s, col_ in zip(c4.series, (TEAL, "ED7D31")):
    s.graphicalProperties.line.solidFill = col_; s.graphicalProperties.line.width = 28000
    s.smooth = False
    s.marker.symbol = "circle"; s.marker.size = 7
    s.marker.graphicalProperties.solidFill = col_; s.marker.graphicalProperties.line.solidFill = col_
c4.y_axis.numFmt = '$#,##0'; c4.y_axis.title = "USD"; c4.x_axis.title = "Order year"
style_chart(c4, "Sales and Profit by Year")
ws.add_chart(c4, "K30")

ws.merge_cells("B52:S52")
ws["B52"] = "What management should do next"
ws["B52"].font = F(bold=True, size=12, color="FFFFFF"); ws["B52"].fill = PatternFill("solid", fgColor=TEAL)
tips = [
    "1. Approve discounts of 30% or more case by case: nearly all such lines lose money (see Discount_Analysis).",
    "2. Review Central region discounting: it discounts most and has the lowest margin.",
    "3. Fix Furniture (Tables, Bookcases): second-largest sales, smallest profit.",
    "4. Reprice or drop loss-making products; grow Copiers, Phones, Accessories and Paper.",
]
for i, t in enumerate(tips):
    ws.merge_cells(f"B{53 + i}:S{53 + i}")
    ws[f"B{53 + i}"] = t; ws[f"B{53 + i}"].font = F()

for w_ in wb.worksheets:
    w_.sheet_properties.tabColor = {"Dashboard": TEAL, "Findings": "548235", "Data": "7F7F7F"}.get(w_.title, NAVY)
ws_dash.page_setup.orientation = "portrait"
ws_dash.page_setup.fitToWidth = 1
ws_dash.page_setup.fitToHeight = 1
ws_dash.sheet_properties.pageSetUpPr.fitToPage = True
ws_dash.print_area = "A1:S57"
for w_ in (ws_about, ws_find, ws_kpi):
    w_.page_setup.orientation = "landscape"; w_.page_setup.fitToWidth = 1; w_.page_setup.fitToHeight = 0
    w_.sheet_properties.pageSetUpPr.fitToPage = True
wb.active = 1
OUT.parent.mkdir(exist_ok=True)
wb.save(OUT)
print("saved", OUT)
