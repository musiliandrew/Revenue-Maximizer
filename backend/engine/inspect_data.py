import pandas as pd
from sqlalchemy import create_engine
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
data['loan_default'] = data['loan_default'].astype(int)

# Summary statistics
print("Dataset Shape:", data.shape)
print("\nSummary Statistics:")
print(data.describe())
print("\nMissing Values:")
print(data.isnull().sum())
print("\nClass Distribution:")
print(data['loan_default'].value_counts(normalize=True))
print("\nFeature Correlations with loan_default:")
numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
print(data[numeric_cols].corr()['loan_default'].sort_values(ascending=False))

# Save to CSV for inspection
data.to_csv('/app/data_inspection.csv', index=False)
print("Data saved to /app/data_inspection.csv")