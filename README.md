diabetic Ensembles

QUICK REFERENCE — WHAT NEVER TOUCHES TEST DATA
===============================================
Imputation median      → computed on X_train only
Scaler .fit()          → called on X_train only
GridSearchCV.fit()     → called on X_train only
KFold / StratifiedKFold → splits X_train only
Calibration .fit()     → called on X_train only

Test set is used exactly once:
→ final evaluate_model() call
→ confusion matrix
→ PR / ROC curves
→ McNemar significance test


