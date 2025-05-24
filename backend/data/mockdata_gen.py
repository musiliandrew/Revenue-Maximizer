import pandas as pd
import numpy as np
import os

# Set seed for reproducibility
np.random.seed(42)

# Parameters
n_customers = 1000
n_card_transactions = 5000  # More transactions than customers
output_dir = "backend/data"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Mock Client Segments
customer_ids = np.arange(1, n_customers + 1)
ages = np.random.randint(22, 65, size=n_customers)
incomes = np.abs(np.random.normal(loc=120000, scale=40000, size=n_customers)).astype(int)
credit_scores = np.clip(np.random.normal(loc=650, scale=70, size=n_customers), 300, 850).astype(int)
is_diaspora = np.random.choice([0, 1], size=n_customers, p=[0.85, 0.15])
segments = np.where(incomes > 200000, 'High Net Worth', 
            np.where(incomes > 100000, 'Middle Class', 'Low Income'))
preferred_currency = np.random.choice(['USD', 'EUR', 'GBP', 'KES'], size=n_customers, p=[0.4, 0.2, 0.1, 0.3])

# Loans Dataset
loan_amounts = np.abs(np.random.normal(loc=300000, scale=100000, size=n_customers)).astype(int)
loan_amounts = np.maximum(loan_amounts, 1)
loan_tenures = np.random.choice([12, 24, 36, 48], size=n_customers)
interest_rates = np.round(np.random.uniform(10, 20, size=n_customers), 2)
loan_defaults = np.random.choice([0, 1], size=n_customers, p=[0.88, 0.12])

# Savings Accounts
savings_balance = np.random.exponential(scale=100000, size=n_customers).astype(int)
monthly_deposit = (savings_balance * np.random.uniform(0.01, 0.05, n_customers)).astype(int)
activity_score = np.random.uniform(0, 1, n_customers)

# FX Usage
fx_volume_usd = np.round(np.random.exponential(scale=500, size=n_customers), 2)

# Card Transactions
card_customer_ids = np.random.choice(customer_ids, size=n_card_transactions, replace=True)
transaction_values = np.round(np.random.exponential(scale=100, size=n_card_transactions), 2)  # Small transactions
categories = np.random.choice(['Retail', 'Travel', 'Dining', 'Online', 'Utilities'], size=n_card_transactions, p=[0.3, 0.2, 0.2, 0.2, 0.1])
is_fx_transaction = np.random.choice([0, 1], size=n_card_transactions, p=[0.8, 0.2])  # 20% involve FX

# Create separate DataFrames
customers_df = pd.DataFrame({
    'customer_id': customer_ids,
    'age': ages,
    'income': incomes,
    'credit_score': credit_scores,
    'is_diaspora': is_diaspora,
    'segment': segments,
    'preferred_currency': preferred_currency
})

loans_df = pd.DataFrame({
    'customer_id': customer_ids,
    'loan_amount': loan_amounts,
    'loan_tenure_months': loan_tenures,
    'interest_rate': interest_rates,
    'loan_default': loan_defaults
})

savings_accounts_df = pd.DataFrame({
    'customer_id': customer_ids,
    'savings_balance': savings_balance,
    'monthly_deposit': monthly_deposit,
    'activity_score': activity_score
})

fx_transactions_df = pd.DataFrame({
    'customer_id': customer_ids,
    'fx_volume_usd': fx_volume_usd
})

card_transactions_df = pd.DataFrame({
    'customer_id': card_customer_ids,
    'transaction_value': transaction_values,
    'category': categories,
    'is_fx_transaction': is_fx_transaction
})

# Save to separate CSV files
customers_df.to_csv(os.path.join(output_dir, "customers.csv"), index=False)
loans_df.to_csv(os.path.join(output_dir, "loans.csv"), index=False)
savings_accounts_df.to_csv(os.path.join(output_dir, "savings_accounts.csv"), index=False)
fx_transactions_df.to_csv(os.path.join(output_dir, "fx_transactions.csv"), index=False)
card_transactions_df.to_csv(os.path.join(output_dir, "card_transactions.csv"), index=False)

print(f"Mock NCBA datasets generated in {output_dir}:")
print(f"- customers.csv")
print(f"- loans.csv")
print(f"- savings_accounts.csv")
print(f"- fx_transactions.csv")
print(f"- card_transactions.csv")