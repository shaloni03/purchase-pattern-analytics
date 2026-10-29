# Importing necessary libraries.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import text
import seaborn as sns

from data_connection import db_connect, TABLE

# getting db connection.
engine = db_connect()

# reading data from given database using pandas read sql
data = pd.read_sql(f"select * from {TABLE}", engine)

# printing information about the data.
# print(data)

# printing shape of the data (rows, columns)
print(data.shape) 

# getting first 5 rows from the data.
print(data.head())

# Printing necessary information about the data.
print(data.info())

# converting string of date to datetime object.
data["Present_Date"] = pd.to_datetime(data["Present_Date"], format= "%d-%m-%Y %H:%M")
print(data.info())

print(data.describe())

# getting revenue from quantity and price.
data["Revenue"] = data["Quantity"] * data["Price"]

for col in ["Quantity", "Price"]:
     print(col)
     print(data[col].mean())
     print(data[col].median())
     print(data[col].mode())
    

# getting how many products or items are there.
# it will be our basket size.
basket_size = data.groupby("BillNo")["Itemname"].nunique()

print(basket_size.describe())
print(data["Itemname"].value_counts().head(10))
print(data["Country"].value_counts().head(5))


# Presenting the plot for quantity per row.
plt.figure(figsize=(8, 4))
plt.hist(data[data["Quantity"].between(1, 50)]["Quantity"],
          bins=50, color="steelblue", edgecolor="white")
plt.title("Quantity per row")
plt.xlabel("Quantity")
plt.ylabel("Number of rows")
plt.savefig("Quantity_per_row.png")
plt.show()


# presenting the plot for Price
plt.figure(figsize=(8, 3))
plt.boxplot(data["Price"].clip(upper=50), vert=False)
plt.title("Price (capped at 50)")
plt.xlabel("Price")
plt.savefig("Price_(capped at 50).png")
plt.show()

basket_size.clip(upper=100).plot(kind="hist", bins=50, title="Products per basket"); 
plt.savefig("Products_per_basket.png")
plt.show()


monthly = data.set_index("Present_Date")["Revenue"].resample("ME").sum()

# plot for monthly revenue.
plt.figure(figsize=(9, 4))
plt.plot(monthly.index, monthly.values, marker="o")
plt.title("Monthly revenue")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("Monthly_revenue.png")
plt.show()

# plot of top 10 products.
top10 = data["Itemname"].value_counts().head(10).sort_values()
plt.figure(figsize=(9, 5))
plt.barh(top10.index, top10.values, color="steelblue")
plt.title("Top 10 products")
plt.xlabel("Number of rows")
plt.tight_layout()
plt.savefig("Top_10_products.png")
plt.show()


# plot for rows by hour
by_hour = data["Present_Date"].dt.hour.value_counts().sort_index()
plt.figure(figsize=(9, 4))
plt.bar(by_hour.index, by_hour.values, color="steelblue")
plt.title("Rows by hour")
plt.xlabel("Hour of the day")
plt.ylabel("Number of rows")
plt.xticks(by_hour.index)
plt.savefig("Rows_by_hour.png")
plt.show()

# getting total null values
print("Total Null Values :: ", data.isnull().sum())

# getting all duplicate rows.
print("Duplicate row:", data.duplicated().sum())

print("Return (BillNo starts with C):",
data["BillNo"].astype(str).str.startswith("C").sum())

print("Negative quantity:", (data["Quantity"] < 0).sum())
print("Zero or negative price:", (data["Price"] <= 0).sum())

for col in ["Quantity", "Price"]:
    q1 = data[col].quantile(0.25)
    q3 = data[col].quantile(0.75)
    low = q1 - 1.5 * (q3 - q1)
    high = q3 + 1.5 * (q3 - q1)
print(col, "normal range:", low, "to", high,
    "| outliers:", ((data[col] < low) | (data[col] > high)).sum())


print(data[data["Itemname"].astype(str).str.upper().str.contains
           ("POSTAGE|MANUAL|DISCOUNT|BANK CHARGES|CARRIAGE|AMAZON FEE")]
    ["Itemname"].unique())



log = []

def record(step, before, after):
    log.append({"step": step, 
    "rows_before": before, 
    "rows_after": after,
    "rows_removed": before - after})

clean = data.copy()

n = len(clean)                                   
clean["BillNo"] = clean["BillNo"].astype(str).str.strip()
clean["Itemname"] = clean["Itemname"].astype(str).str.strip().str.upper()
clean = clean.replace({"": np.nan, "NAN": np.nan, "NONE": np.nan})
clean = clean.dropna(subset=["BillNo", "Itemname"])
record("Remove empty BillNo/Itemname", n, len(clean))

n = len(clean)
clean = clean.drop_duplicates()
record("Remove duplicates", n, len(clean))

n = len(clean)
clean = clean[~clean["BillNo"].str.startswith("C")]
clean = clean[(clean["Quantity"] > 0) & (clean["Price"] > 0)]
record("Remove returns, zero or negative Quantity/Price", n, len(clean))

n = len(clean)
fees = "POSTAGE|MANUAL|DISCOUNT|BANK CHARGES|CARRIAGE|AMAZON FEE|CRUK COMMISSION|ADJUST"
clean = clean[~clean["Itemname"].str.contains(fees, regex=True)]
record("Remove fee rows", n, len(clean))

n = len(clean)
clean = clean[(clean["Quantity"] <= clean["Quantity"].quantile(0.999)) & (clean["Price"] <= 
                                                                          clean["Price"].quantile(0.999))]
record("Remove outliers", n, len(clean))

n = len(clean)
item_baskets = clean.groupby("Itemname")["BillNo"].nunique()
clean = clean[clean["Itemname"].isin(item_baskets[item_baskets >= 30].index)]
record("Remove rare products (< 30 baskets)", n, len(clean))

n = len(clean)
basket_items_count = clean.groupby("BillNo")["Itemname"].nunique()
clean = clean[clean["BillNo"].isin(basket_items_count[basket_items_count >= 2].index)]
record("Remove 1-product baskets", n, len(clean))

clean = clean.reset_index(drop=True)
print(pd.DataFrame(log))



basket = (clean.groupby(["BillNo", "Itemname"])["Quantity"].sum().unstack(fill_value=0) > 0)
print(basket.shape)

clean.to_csv("cleaned_transactions.csv", index=False)
basket.to_csv("basket_matrix.csv")
pd.DataFrame(log).to_csv("cleaning_log.csv", index=False)


# plot for top 15 products
support_single = basket.mean().sort_values(ascending=False)
support_single.head(15).sort_values().plot(kind="barh", figsize=(9,6),
title="Top 15 products (share of baskets)")
plt.tight_layout() 
plt.savefig("Top_15_products_(share of baskets).png")
plt.show()

# plot for products which brought together from top 15
top_items = support_single.head(15).index
b = basket[top_items].astype(int)
co = b.T.dot(b)
print(co)
co = co.mask(np.eye(len(co), dtype=bool), 0) 
plt.figure(figsize=(10,8))
sns.heatmap(co, cmap="Blues"); 
plt.title("Bought together (top 15)")
plt.tight_layout(); 
plt.savefig("Bought_together_(top 15).png")
plt.show()

# Trend: baskets per month for the top 5 products
top5 = support_single.head(5).index
trend = (clean[clean["Itemname"].isin(top5)].assign(month=lambda d: 
d["Present_Date"].dt.to_period("M").astype(str)).groupby(["month", "Itemname"])["BillNo"].nunique().unstack(fill_value=0))
trend.plot(figsize=(10,5), marker="o", title="Monthly baskets, top 5 products"); 
plt.savefig("Monthly_baskets,_top_5_products.png")
plt.show()

# Using apriori algorithm
from mlxtend.frequent_patterns import apriori, association_rules
frequent = apriori(basket, min_support=0.015, use_colnames=True, max_len=3, low_memory=True)
print(len(frequent), "frequent sets")
print(frequent.sort_values("support", ascending=False).head(10))

rules = association_rules(frequent, metric="lift", min_threshold=1.0)
rules["antecedents"] = rules["antecedents"].apply(lambda s: ","
 .join(sorted(s)))
rules["consequents"] = rules["consequents"].apply(lambda s: ","
 .join(sorted(s)))
print(rules[["antecedents", "consequents", "support", "consequents", "lift"]].head(15))

rules[["antecedents", "consequents", "support", "consequents", "lift"]].to_csv("apriori_rules.csv", index=False)


# scatterplot for association rules
sns.scatterplot(data=rules, x="support", y="confidence", size="lift",
hue="lift", palette="viridis", sizes=(30,300))
plt.title("Association rules")
plt.savefig("Association_rules.png")
plt.show()

top = rules.head(10).copy()
top["rule"] = top["antecedents"] + " -> " + top["consequents"]
top.sort_values("lift").plot(kind="barh", x="rule", y="lift", figsize=(10,6), 
                             legend=False, title="Top 10 rules by lift")
plt.tight_layout()
plt.savefig("Top_10_rules_by-lift")
plt.show()


# plot for lift between the product
single = rules[~rules["antecedents"].str.contains(",") & ~rules["consequents"].str.contains(",")]

# keep the top 25 products by their highest lift
top_items = (
    single.groupby("antecedents")["lift"].max()
    .nlargest(25).index
)

single = single[single["antecedents"].isin(top_items) & single["consequents"].isin(top_items)]
heat = single.pivot_table(index="antecedents", columns="consequents", values="lift")
plt.figure(figsize=(12,12))
sns.heatmap(heat, cmap="YlOrRd", xticklabels=True,
    yticklabels=True, linewidths=0.3)
plt.title("Lift between products")
plt.tight_layout()
plt.savefig("Lift_between_products.png")
plt.show()


print("Baskets:", basket.shape[0], "| Products:", basket.shape[1])
print("Average products per basket:", round(basket.sum(axis=1).mean(), 1))
print("Rules kept:", len(rules))
print("Strongest rule:" ,rules.loc[0,"antecedents"], "->", rules.loc[0,"consequents"], 
      "| lift", round(rules.loc[0, "lift"], 2))


# summarized values.
summary = rules[["antecedents", "consequents", "support", "confidence", "lift"]].head(10).round(3)
print(summary)

summary.to_csv("top10_rules.csv", index=False)


price = clean.groupby("Itemname")["Price"].median()

n = len(basket)
reco = rules[~rules["consequents"].str.contains(",")].copy()
reco["price_b"] = reco["consequents"].map(price)
reco["baskets_with_A"] = reco["antecedent support"] * n
reco["A_without_B"] = reco["baskets_with_A"] * (1 - reco["confidence"])
uptake = 0.05
reco["extra_revenue"] = reco["A_without_B"] * reco["price_b"]

# categorizing 
def action(r):
    if r["lift"] >= 3 and r["confidence"] >= 0.5:
        return "Bundle"
    if r["lift"] >= 2:
        return "Cross-sell"
    return "Promotion"

reco["action"] = reco.apply(action, axis=1)
out = reco.sort_values("extra_revenue", ascending=False)[["antecedents", "consequents", "confidence","lift", "action", "extra_revenue"]].head(10).round(2)
print(out)

out.to_csv("recommendations.csv", index=False)