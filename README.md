# Purchase Pattern Analytics (Market Basket Analysis)

Market Basket Analysis on a year of retail transactions (1 Dec 2010 to 9 Dec 2011, 522,064 rows) using EDA, rule-based cleaning, the Apriori algorithm and Power BI, to find products bought together and turn them into recommendations.

## Headline results
- 494,747 rows kept after cleaning (94.8%); 17,750 bills x 2,559 products in the basket matrix
- 890 frequent itemsets and 926 association rules (min support 1.5%, lift >= 1)
- Strongest links: Bakelike alarm clock colours (lift ~12) and cake-case designs (lift up to 9); party and baking items lead to the Regency Cakestand (lift 2.1 to 2.5)

## Structure
```
src/                  data_connection.py, data_project.py   (analysis pipeline)
notebooks/            Data_Project.ipynb                    (same analysis with outputs)
data/processed/       cleaning_log.csv, top10_rules.csv, recommendations.csv
reports/figures/      12 charts
docs/                 01 Kick-off summary
                      02 EDA report and domain analysis
                      03 Data cleaning documentation
                      04 Apriori implementation and visualisation report
                      05 Insights and recommendations report
                      06 Final project documentation
                      07 Review and iteration log
presentation/         Stakeholder slide deck (.pptx)
dashboards/powerbi/   Power BI file goes here
```

## Run
```bash
pip install -r requirements.txt
mkdir outputs && cd outputs
MPLBACKEND=Agg python ../src/data_project.py
```
Requires network access to the project MySQL database configured in `src/data_connection.py`. Outputs (CSVs and PNGs) are written to `outputs/`.