import pandas as pd
from sqlalchemy import create_engine
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import pickle
import os
from decimal import Decimal

# Database connection
engine = create_engine('postgresql://postgres:2003@db:5432/revenue')

# Load data
query = """
SELECT l.loan_id, l.loan_amount, l.interest_rate, l.loan_tenure_months, 
       c.income, c.credit_score, l.loan_default, s.activity_score,
       c.is_diaspora, c.age, c.segment,
       COALESCE((
           SELECT SUM(ct.transaction_value)
           FROM card_transactions ct
           WHERE ct.customer_id = c.customer_id
       ), 0) as total_card_value
FROM loans l
JOIN customers c ON l.customer_id = c.customer_id
LEFT JOIN savings_accounts s ON c.customer_id = s.customer_id
"""
data = pd.read_sql(query, engine)

# Convert Decimal to float
decimal_columns = ['loan_amount', 'interest_rate', 'total_card_value']
for col in decimal_columns:
    data[col] = data[col].apply(lambda x: float(x) if isinstance(x, Decimal) else x)

# Fill missing values
data['activity_score'] = data['activity_score'].fillna(0)
data['total_card_value'] = data['total_card_value'].fillna(0)
data['age'] = data['age'].fillna(data['age'].median())
data['segment'] = data['segment'].fillna('Unknown')

# Encode categorical 'segment'
data = pd.get_dummies(data, columns=['segment'], prefix='segment')

# Convert boolean to int
data['is_diaspora'] = data['is_diaspora'].astype(int)

# Features and target
features = ['loan_amount', 'interest_rate', 'loan_tenure_months', 'income', 'credit_score', 
            'activity_score', 'total_card_value', 'is_diaspora', 'age', 
            'segment_High Net Worth', 'segment_Low Income', 'segment_Middle Class']
X = data[features].astype(float)
y = data['loan_default'].astype(int)

# Calculate scale_pos_weight for class imbalance
neg_count = len(y[y == 0])
pos_count = len(y[y == 1])
scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
model = XGBClassifier(
    random_state=42,
    eval_metric='auc',
    max_depth=3,
    learning_rate=0.1,
    n_estimators=100,
    scale_pos_weight=scale_pos_weight
)
model.fit(X_train_scaled, y_train)

# Evaluate
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
auc = roc_auc_score(y_test, y_pred_proba)
print(f"Model AUC-ROC: {auc:.2f}")

# Save model and scaler
os.makedirs('/app/models', exist_ok=True)
with open('/app/models/loan_risk_model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('/app/models/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

print("Model and scaler saved successfully")