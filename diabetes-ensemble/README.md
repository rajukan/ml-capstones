# Diabetes Prediction — Ensemble Models vs. Paper's Logistic Regression Baseline

This project reproduces and extends a published logistic-regression approach to
diagnosing diabetes from the Pima Indians Diabetes dataset (`Diabetic.csv`),
then compares it against several ensemble learning methods to find the most
clinically useful model for a screening tool.

## Dataset & EDA

- 768 records, 8 clinical features (Pregnancies, Glucose, BloodPressure,
  SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age) + `Outcome`.
- Class imbalance: 500 negative vs. 268 positive cases (~65% / 35%).
- Several features (Glucose, BloodPressure, SkinThickness, Insulin, BMI)
  contain biologically implausible zeros that act as hidden missing values —
  these were imputed with the column median.
- Insulin and DiabetesPedigreeFunction are heavily right-skewed, motivating
  `RobustScaler` (median/IQR) over `StandardScaler`.
- A `Glucose_Age` interaction feature was engineered after imputation, since
  glucose risk is more pronounced at older ages.
- A Random Forest feature-importance pass confirmed the paper's 5 key
  predictors (Glucose, BMI, Age, DiabetesPedigreeFunction, Pregnancies) plus
  the new `Glucose_Age` feature as the most informative.

## Methodology

- **Train/test split**: 70/30, stratified, `random_state=42`.
- **Decision threshold**: 0.35 (instead of the default 0.5) to favor recall —
  in a screening context, missing a diabetic patient (false negative) is far
  costlier than a false positive.
- **Tuning objective**: `average_precision` (AUPRC), which is robust to class
  imbalance and focuses on ranking the minority (diabetic) class.
- Evaluation via 5-fold stratified cross-validation and an independent holdout
  test set, reporting Accuracy, Precision, Recall, F1, AUC, and AUPRC.

## Models Compared

| Model | Description |
|---|---|
| **Paper Tuned (LR)** | Logistic Regression on the paper's 5 predictors + `Glucose_Age`, tuned via `GridSearchCV`. Reproduces the paper's baseline. |
| **Decision Tree Validator** | A single tuned Decision Tree on the same 5 predictors, used as an interpretable sanity check. |
| **Ensemble 1 — Soft Voting** | Combines 7 tuned base learners (LR, SVM, KNN, Naive Bayes, MLP, Random Forest, Gradient Boosting) via soft (probability-averaged) voting. |
| **Ensemble 2 — Bagging** | 100+ Decision Trees trained on bootstrap samples (`BaggingClassifier`), tuned via grid search over `n_estimators`, `max_samples`, `max_features`. |
| **Ensemble 3 — Stacking** | Tuned Random Forest + Gradient Boosting base learners feeding a Logistic Regression meta-learner, tuned with `HalvingGridSearchCV`. |

## Results (Test Set, threshold = 0.35)

| Model | Accuracy | Precision | Recall | F1 | AUC | AUPRC |
|---|---|---|---|---|---|---|
| Paper Tuned (LR) | 0.762 | 0.648 | 0.704 | 0.675 | 0.839 | 0.717 |
| Decision Tree Validator | 0.714 | 0.566 | 0.790 | 0.660 | 0.783 | 0.639 |
| Soft Voting Ensemble | 0.753 | 0.620 | 0.765 | 0.685 | 0.842 | 0.735 |
| Bagging Ensemble | 0.749 | 0.607 | **0.802** | **0.691** | 0.833 | 0.711 |
| Stacking Ensemble | 0.749 | 0.635 | 0.667 | 0.651 | 0.840 | 0.732 |

**Calibration (mean calibration error, lower is better):** Bagging (0.064) <
Logistic Regression (0.083) < Stacking (0.091) < Soft Voting (0.108). All
models were recalibrated (Platt scaling for LR, isotonic for the ensembles).

## Conclusion

A composite clinical score (50% AUPRC, 30% Recall, 20% Precision) was used to
select the best model. **Bagging Ensemble** wins: it has the highest recall
(~80% of diabetic patients correctly identified), the best probability
calibration, and the best F1 score, making it the most suitable model for a
diabetes screening tool where missed diagnoses are the most costly error.
Soft Voting and Stacking improve ranking (AUPRC) over the LR baseline but
either need extra calibration (Soft Voting) or lose recall (Stacking).

The winning model is saved to `models/bagging_ensembles.pkl`.

## Model Serving

A Streamlit app (`diabetic_serving.py`) loads the saved model and serves
predictions interactively. Run it from this directory with:

```
python -m streamlit run .\diabetic_serving.py
```

## Files

- `gyan-capstone-1-ensembles.ipynb` / `.html` — full analysis notebook (EDA,
  preprocessing, model training, evaluation, calibration).
- `Diabetic.csv`, `Diabetic-2.csv` — dataset(s).
- `models/bagging_ensembles.pkl` — trained, best-performing model.
- `diabetic_serving.py` — Streamlit serving app.
- `milestones/` — project milestone documents and presentations.
