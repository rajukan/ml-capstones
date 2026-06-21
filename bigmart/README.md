# BigMart Sales — Prediction & Anomaly Detection

This project works with the BigMart sales dataset across two notebooks:

## `Big-mart-sales-prediction.ipynb`

End-to-end regression pipeline: EDA, missing-value imputation (`Item_Weight`,
`Item_Visibility`, `Outlet_Size`), outlier capping on `Item_Visibility`,
feature engineering (MRP/weight bins, calorie estimates, outlet age/status,
item frequency), label/ordinal encoding shared consistently between train and
test sets, and standard scaling. Several regressors are compared
(Linear/Ridge/Lasso, Decision Tree, Random Forest, Gradient Boosting,
AdaBoost, Bagging), with a Bagging ensemble of tuned Gradient Boosting models
as the final predictor (RMSE ~1066 on the validation split).

## `Big-mart-sales-pyod.ipynb`

Anomaly detection on the same dataset using [PyOD](https://github.com/yzhao062/pyod),
reusing the prediction notebook's imputation steps but **without** the
outlier-capping step (since finding outliers is the point here).

### Bivariate analysis (`Item_MRP` vs `Item_Outlet_Sales`)

Seven detectors (ABOD, CBLOF, Feature Bagging, HBOS, Isolation Forest, KNN,
Average KNN) are fit on just these two scaled features, with decision-boundary
contour plots for each. ABOD gives the best separation (silhouette ≈ 0.29).

### Multivariate analysis

Isolation Forest is run on a wider feature set (`Item_Weight`,
`Item_Visibility`, `Item_MRP`, `Item_Outlet_Sales`, `Item_Fat_Content`,
`Item_Type`, `Outlet_Size`, `Outlet_Location_Type`, `Outlet_Type`,
`Outlet_Age`), so "unusual" is judged relative to the full operational
context rather than just the price/sales relationship. 5% of rows (427/8523)
are flagged.

**Findings:**

- **Anomalies concentrate heavily in a few outlets**: `OUT019` (27% of its
  rows flagged) and `OUT027` (14%) — both far above the ~5% baseline.
  `OUT013` and `OUT010` are next (5.8–6.7%); the remaining six outlets are
  all under 4%.
- **By outlet type**: Grocery Store (16%) and Supermarket Type3 (14%) have
  much higher anomaly rates than Supermarket Type1 (1.6%) and Type2 (3.8%).
  This lines up with `OUT019`/`OUT010` (Grocery Stores) and `OUT027`
  (the only Supermarket Type3) driving most of the flagged rows.
- **Most flagged rows pair a high `Item_MRP` with sales far from the
  median** — either unusually high sales for a premium item at
  Supermarket Type3 stores, or near-zero sales for items at Grocery Stores
  (`OUT019`), suggesting Grocery Store sales volumes are systematically
  out of step with the price/feature patterns learned from supermarkets.
- **By item type**: Seafood, Starchy Foods, Baking Goods, and Breakfast
  have the highest anomaly rates (10–13%), though these are also the
  smallest categories by row count.

These results suggest `OUT019`, `OUT010`, and `OUT027` may warrant separate
treatment (or a per-outlet-type model) in the prediction pipeline, since their
sales patterns diverge most from the rest of the chain.

## Setup

```
pip install -r ../requirements.txt
```
