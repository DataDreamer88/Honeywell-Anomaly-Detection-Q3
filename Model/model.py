# Step 1: Imports and Load Data
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset (already balanced by you)
df = pd.read_csv(r"G:\Projects\honeywell\Anomalyze\DataProcessing\exported_data.csv")

# --- Shuffle dataset to remove sequential bias ---
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Drop non-feature columns
exclude_cols = ['number', 'Timestamp', 'Anomaly', 'Parameter for Anomaly', 'Actual value', 'Run id']
features = df.drop(columns=exclude_cols)
target = df['Anomaly']

# Step 2: Train-test split (by Run id to avoid leakage)
unique_runs = df['Run id'].unique()
train_runs, test_runs = train_test_split(
    unique_runs,
    test_size=0.2,
    random_state=42,
    stratify=df.groupby('Run id')['Anomaly'].first()
)

train_idx = df['Run id'].isin(train_runs)
test_idx = df['Run id'].isin(test_runs)

X_train, y_train = features[train_idx], target[train_idx]
X_test, y_test = features[test_idx], target[test_idx]

print(f"Train size: {X_train.shape}, Test size: {X_test.shape}")

# Step 3: Create DMatrix (no class weights now, dataset already balanced)
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

# Step 4: Model parameters (same tuning, but no class weights needed)
params = {
    'objective': 'multi:softprob',
    'num_class': len(np.unique(y_train)),
    'eval_metric': ['mlogloss', 'merror'],
    'eta': 0.05,
    'max_depth': 8,
    'min_child_weight': 5,
    'gamma': 1.0,
    'subsample': 0.7,
    'colsample_bytree': 0.7,
    'lambda': 2,
    'alpha': 1,
    'seed': 42
}

# Step 5: Training with longer early stopping patience
evals = [(dtrain, 'train'), (dtest, 'eval')]
bst = xgb.train(
    params,
    dtrain,
    num_boost_round=1000,
    evals=evals,
    early_stopping_rounds=50,
    verbose_eval=50
)

# Step 6: Predictions
y_pred_prob = bst.predict(dtest, iteration_range=(0, bst.best_iteration + 1))
y_pred = np.argmax(y_pred_prob, axis=1)

# Step 7: Evaluation
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report (macro/weighted F1 included):")
print(classification_report(y_test, y_pred, digits=4))
print("Macro F1:", f1_score(y_test, y_pred, average='macro'))
print("Weighted F1:", f1_score(y_test, y_pred, average='weighted'))
print("\nAccuracy:", accuracy_score(y_test, y_pred))

# Step 8: Confusion Matrix Visualization
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Normal', 'Freeze', 'Step', 'Ramp'],
            yticklabels=['Normal', 'Freeze', 'Step', 'Ramp'])
plt.xlabel('Predicted')
plt.ylabel('True Label')
plt.title('Confusion Matrix - XGBoost Anomaly Classification')
plt.show()


import joblib

# Save the trained XGBoost model
joblib.dump(bst, "anomaly_detector.pkl")