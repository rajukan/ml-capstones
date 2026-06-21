# BigMart Sales — Prediction & Anomaly Detection

This project works with the BigMart sales dataset across two notebooks, plus a
standalone modeling script.

## `Big-mart-sales-prediction.ipynb`

Pipeline order (rebuilt to keep every fitted statistic train-only and avoid
leakage): train/test split → basic cleaning → outlier capping (train-only IQR
bounds, run *before* anything derived from those columns) → feature
engineering (MRP/weight bins, calorie estimates, outlet age/status, item
frequency) → skew check with log/sqrt transforms → label/ordinal encoding →
standard scaling → feature selection → modeling.

Feature selection is a 3-stage pipeline computed on the training split only:
drop pairwise-redundant features (correlation > 0.8, keep whichever side
correlates more strongly with the target), univariate significance (ANOVA for
categorical columns, Pearson for continuous), and an embedded check
(`SelectFromModel(LinearRegression())` on fully-scaled features). The three
checks are combined into an Agreement score; the consensus core
(Agreement = 2) is `Item_MRP`, `Outlet_Size`, `Outlet_Location_Type`,
`Outlet_Type`.

The target (`Item_Outlet_Sales`) is log-transformed before modeling and
predictions are exponentiated back to the real sales scale — this keeps
predictions non-negative and fits the right-skewed target much better than
modeling on the raw scale (R² 0.74 vs 0.60 without the transform).

Several regressors are compared via 5-fold CV (see `model_comparison.py`):
Linear/Ridge/Lasso, Decision Tree, Random Forest, Gradient Boosting,
AdaBoost, and a Bagging ensemble of a tuned Gradient Boosting model. Bagging
and Gradient Boosting are statistically tied as the best performers (holdout
RMSE ≈ 0.52 on the log scale, R² ≈ 0.74); `GridSearchCV` tuning does not
meaningfully beat sklearn's defaults for Gradient Boosting. Lasso at its
default alpha is unstable on the log-scale target (collapses to R² ≈ 0) —
a known open issue, needs `LassoCV`.

Back-transformed final predictions have no negative values, but the mean
runs ~11% below the real training mean — a known bias from `exp()`
retransformation (Jensen's inequality) that isn't yet corrected (e.g. via
Duan's smearing estimator).

### `model_comparison.py`

Standalone module with no notebook dependency: it loads the engineered
feature matrices the notebook exports (`data/X_train_features.csv`,
`data/y_train.csv`, `data/X_test_features.csv`) and runs the model
comparison / tuning / final-fit pipeline described above. Run directly via:

```
python model_comparison.py
```

from inside `bigmart/`; writes `data/predictions.csv`.

## `Big-mart-sales-pyod.ipynb`

Anomaly detection on the same dataset using [PyOD](https://github.com/yzhao062/pyod).
Loads the prediction notebook's precleaned-but-uncapped export
(`data/train_precleaned.csv`) directly instead of re-deriving cleaning logic,
since PyOD's job is to find the outliers that the other notebook caps —  it
must never see data downstream of that capping step.

### Bivariate analysis (`Item_MRP` vs `Item_Outlet_Sales`)

Seven detectors (ABOD, CBLOF, Feature Bagging, HBOS, Isolation Forest, KNN,
Average KNN) are fit on just these two scaled features, with decision-boundary
contour plots for each. ABOD gives the best separation (silhouette ≈ 0.29).

### Multivariate analysis

The same 7 detectors are re-run on a wider feature set (`Item_Weight`,
`Item_Visibility`, `Item_MRP`, `Item_Outlet_Sales`, `Outlet_Age`, plus
one-hot-encoded `Item_Type`/`Outlet_Type`/`Item_Fat_Content` and ordinal
`Outlet_Size`/`Outlet_Location_Type`). Nominal columns are one-hot encoded
rather than label-encoded, since integer codes would fabricate a false
ordinal distance for the distance-based detectors (KNN, Feature Bagging,
CBLOF). Isolation Forest wins (silhouette ≈ 0.113); 5.0% of rows (427/8523)
are flagged, with 67 corroborated by ≥4 of the 7 detectors
(`high_confidence_anomaly`).

**Findings** (one-sided binomial tests against the 5% baseline rate,
deduplicated for nested/overlapping segments — see
`lessons-learnt-bigmart-pyod.txt` item 13):

- **Non-consumable items** (`Item_Identifier_Type == 'NC'`) are the single
  strongest signal: 17.7% anomaly rate vs. the 5% baseline (p ≈ 1.5e-75).
  This subsumes three `Item_Type` categories (Others, Household, Health and
  Hygiene) that looked independently significant but are exactly the NC
  population restated under a different grouping.
- **OUT018** and **OUT019** run 3.9–4.2x the baseline rate (19.5%, 21.0%;
  p = 2.4e-55, p = 8.8e-38).
- **OUT027** (the only Supermarket Type3) is 1.7x baseline (8.6%,
  p = 3.3e-6) — a distinct signal, not nested in the outlet/NC findings above.
- **Seafood** items are independently elevated (p = 7.0e-5) once the NC
  overlap is removed.

These results suggest non-consumable items and outlets OUT018/OUT019/OUT027
may warrant separate treatment (or a per-segment model) in the prediction
pipeline, since their sales patterns diverge most from the rest of the chain.

## Setup

```
pip install -r ../requirements.txt
```
