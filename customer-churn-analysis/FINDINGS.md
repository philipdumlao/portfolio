# Findings and Recommendations

All numbers come from `src/02_eda_segments.py` (see `outputs/key_metrics.txt` and `outputs/segment_analysis.csv`).
These are **associations in historical data, not proof of cause**.

## Headline numbers
- 7,043 customers, **1,869 churned = 26.54% overall churn rate**.
- Churned customers had a mean tenure of 18.0 months (median 10) vs 37.6 months (median 38) for retained customers.
- Churned customers pay more: mean monthly charge $74.44 vs $61.27.
- Churned customers represent **$139,131 of $456,117 monthly recurring revenue (30.5%)**, more than their 26.5% share of customers.

## Findings
1. **Contract type is the strongest separator.** Month-to-month churn is 42.71% (1,655 of 3,875), one-year 11.27%, two-year 2.83%. Month-to-month customers are 55% of the base but **88.55% of all churn**.
2. **Fiber optic customers churn at 41.89%** (1,297 of 3,096) vs 18.96% for DSL and 7.40% for no internet. Fiber is 44% of customers but **69.40% of churners**.
3. **Electronic check payers churn at 45.29%** (1,071 of 2,365) vs 15.24% to 19.11% for the other three methods. They are 57.30% of all churners. Automatic payment methods (bank transfer 16.71%, credit card 15.24%) are the most stable.
4. **Early tenure is the danger zone.** 0-12 months churn is 47.44% (1,037 of 2,186) and holds 55.48% of all churn; 49-72 months is only 9.51%.
5. **Monthly charge has a non-linear relationship.** Churn is highest in the $70-90 band (37.80%, 697 churned) and $90+ band (32.78%), lowest at or under $35 (10.89%). Fig 7 shows that within fiber, even the $35-70 band churns at 62.5% (n=112), so price alone does not explain it.
6. **Support and security add-ons are associated with lower churn.** Customers with internet but no tech support churn at 41.64% vs 15.17% with it; no online security 41.77% vs 14.61% with it. Customers who take these add-ons may differ in other ways, so this is not proof that the add-ons reduce churn.
7. **Combined segments are far riskier than any single factor.** Month-to-month + fiber: 54.61% churn (2,128 customers, 62.17% of all churn). Month-to-month + tenure 0-12 months: 51.35% (1,994 customers). Month-to-month + fiber + tenure up to 12 months: 70.20% churn (916 customers, 34.4% of all churn). Month-to-month + electronic check: 53.73%, holding 53.2% of all churn.
8. **Other associations:** senior citizens 41.68% vs 23.61%; no partner 32.96% vs 19.66%; no dependents 31.28% vs 15.45%; paperless billing 33.57% vs 16.33%. Gender shows almost no difference (26.92% female vs 26.16% male).

## Rate vs contribution (they are different measures)
- **High rate, small volume:** fiber with mailed check (42.64%, 258 customers, 5.89% of churn) and senior citizens (41.68%, 1,142 customers, 25.47% of churn) have high rates but smaller contribution than the contract and fiber segments.
- **Large volume, moderate rate:** DSL month-to-month (32.22%, 1,223 customers) adds 21.08% of churn because of its size.
- **Both high (priority):** month-to-month + fiber, month-to-month in first 12 months, fiber + electronic check.

## Recommendations (in priority order)
1. **Convert month-to-month customers to 12-month contracts**, starting with the month-to-month fiber group (2,128 customers, 62.17% of churn). Offer a discount or bundle in return for the term commitment. Test it against a control group before rolling out.
2. **Build a first-year onboarding and check-in program.** Customers in months 0-12 hold 55.48% of churn. Add proactive contact at roughly months 1, 3 and 6, with extra attention for new fiber customers (70.20% churn).
3. **Investigate fiber service quality and value.** A rate this high with no price-band explanation points to experience, reliability or competition. Review support tickets, outage data and competitor pricing in fiber areas before cutting prices.
4. **Move electronic check payers to automatic payment** with a small incentive. They are 33.6% of customers but 57.30% of churn, and autopay customers churn at 15% to 17%.
5. **Bundle tech support and online security** as a free trial for at-risk internet customers, and measure whether churn falls compared with a holdout group.

## Limitations
- Single snapshot, no dates: cannot measure time-to-churn or seasonality, and tenure is only a proxy.
- No reasons for churn, satisfaction scores, competitor or network-quality data.
- Customers are only compared on the columns present; confounding is likely (for example, fiber customers are also more likely to be month-to-month).
- Tenure and charge bands use fixed cutoffs chosen for readability; other cutoffs may shift the numbers slightly.
- The dataset is an IBM sample and may be synthetic or modified, so results may not generalize to a real operator.
