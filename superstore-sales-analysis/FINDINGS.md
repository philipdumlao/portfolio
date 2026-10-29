# Findings and Recommendations

All figures come from `excel/Superstore_Sales_Performance.xlsx` and are reproduced independently by `src/verify_numbers.py`. Discount results are associations, not proof of cause.

## Key findings

1. Overall: $2,326,534 sales, $292,297 profit, 12.6% margin on 38,654 units. Sales grew from $494,040 (2023) to $745,568 (2026) and profit from $51,684 to $95,926.

2. Regions: West leads both sales ($739,814) and profit ($110,799, 15.0% margin). Central ranks third in sales ($503,171) but last in profit ($39,865, 7.9% margin). South has the lowest sales ($391,722).

3. Categories: Technology ($146,543, 17.4%) and Office Supplies ($126,023, 17.2%) carry the profit. Furniture has $754,748 of sales, more than Office Supplies, but only $19,730 profit (2.6% margin), 6.7% of total profit.

4. Sub-categories: Copiers ($56,094), Phones ($45,051), Accessories ($41,937) and Paper ($34,512) lead profit. Three lose money: Tables (-$17,753), Bookcases (-$3,632) and Supplies (-$1,171). Machines earn only 1.8% margin on $189,925 of sales.

5. Products: 302 of 1,849 products lose money, -$77,600 in total. The biggest losers are Cubify CubeX 3D Printer Double Head Print (-$8,880) and the Lexmark MX611dhe Monochrome Laser Printer (-$4,590). The top product is Canon imageCLASS 2200 Advanced Copier ($25,200).

6. Discounts: lines with no discount earn a 29.6% margin, up to 20% earn 11.5%, while 21-30% (-10.1%), 31-50% (-24.8%) and over 50% (-118.7%) are negative. The line-level correlation between discount and profit is -0.22. Lines at 30%+ discount are 13.9% of all lines, 96.8% of them lose money, and together they total -$136,021 of profit. This is an association; product mix also differs by band (for example Binders account for most lines above 50%), so it does not prove discounts alone cause the losses.

7. Central: average discount is 24.1% vs 10.9% in West, and 27.7% of Central lines carry a 30%+ discount vs 3.6% in West. Central also has the lowest margin (7.9%), consistent with a discounting problem there.

## Recommendations

1. Put an approval step on discounts of 30% or more (and review anything above 50%). These lines are about 14% of volume but lose money on nearly all lines. Test the cap on a subset of orders first to confirm the effect before applying it everywhere.

2. Review Central region discounting practices and compare with West, which discounts far less and earns the highest margin.

3. Fix Furniture profitability: reprice or renegotiate supplier cost for Tables and Bookcases, and reduce discounts on Furniture before cutting volume.

4. Review the loss-making products, starting with the Cubify CubeX 3D printers and Lexmark MX611dhe: reprice, bundle without discount, or stop selling.

5. Protect and grow the high-margin lines (Copiers, Phones, Accessories, Paper) and keep their discounts low, since Technology and Office Supplies earn most of the profit.
