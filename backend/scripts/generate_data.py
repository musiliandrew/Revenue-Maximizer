import pandas as pd
import numpy as np
import os
from decimal import Decimal

# Set seed for reproducibility
np.random.seed(42)

# Parameters
n_customers = 1000
n_card_transactions = 5000
n_loans = 800
n_fx_transactions = 500
output_dir = "/app/data"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Customers (Kenyan demographics)
customer_ids = np.arange(1, n_customers + 1)
ages = np.random.randint(22, 65, size=n_customers)
incomes = np.random.lognormal(mean=10.5, sigma=0.8, size=n_customers).astype(int)  # Median ~KES 50K
credit_scores = np.clip(np.random.normal(loc=650, scale=70, size=n_customers), 300, 850).astype(int)
is_diaspora = np.random.choice([True, False], size=n_customers, p=[0.15, 0.85])
segments = np.where(incomes > 200000, 'High Net Worth',
            np.where(incomes > 100000, 'Middle Class', 'Low Income'))
preferred_currency = np.random.choice(['KES', 'USD', 'EUR', 'GBP'], size=n_customers, p=[0.7, 0.2, 0.05, 0.05])

# Savings Accounts
savings_balance = np.random.exponential(scale=100000, size=n_customers).astype(int)  # Skewed
monthly_deposit = (savings_balance * np.random.uniform(0.01, 0.05, n_customers)).astype(int)
activity_score = np.random.uniform(0, 1, n_customers)

# Card Transactions
card_customer_ids = np.random.choice(customer_ids, size=n_card_transactions, replace=True)
transaction_values = np.round(np.random.exponential(scale=5000, size=n_card_transactions), 2)  # KES
categories = np.random.choice(['Retail', 'Travel', 'Dining', 'Online', 'Utilities'], size=n_card_transactions, p=[0.3, 0.2, 0.2, 0.2, 0.1])
is_fx_transaction = np.random.choice([True, False], size=n_card_transactions, p=[0.2, 0.8])

# Loans
loan_customer_ids = np.random.choice(customer_ids, size=n_loans, replace=True)
loan_amounts = np.random.lognormal(mean=11, sigma=1, size=n_loans).astype(int)  # Median ~KES 100K
loan_tenures = np.random.choice([12, 24, 36, 48], size=n_loans)
interest_rates = np.round(np.random.uniform(10, 20, size=n_loans), 2)  # 10-20%
loan_defaults = np.random.choice([False, True], size=n_loans, p=[0.88, 0.12])  # 12% default

# FX Transactions (diaspora-focused)
fx_customer_ids = np.random.choice(customer_ids[is_diaspora], size=n_fx_transactions, replace=True)
fx_volume_usd = np.round(np.random.exponential(scale=1000, size=n_fx_transactions), 2)  # USD

# Create DataFrames
customers_df = pd.DataFrame({
    'customer_id': customer_ids,
    'age': ages,
    'income': incomes,
    'credit_score': credit_scores,
    'is_diaspora': is_diaspora,
    'segment': segments,
    'preferred_currency': preferred_currency,
    'created_at': pd.Timestamp('2025-01-01'),
    'updated_at': pd.Timestamp('2025-01-01')
})

savings_accounts_df = pd.DataFrame({
    'account_id': range(1, n_customers + 1),
    'customer_id': customer_ids,
    'savings_balance': savings_balance,
    'monthly_deposit': monthly_deposit,
    'activity_score': activity_score,
    'created_at': pd.Timestamp('2025-01-01'),
    'updated_at': pd.Timestamp('2025-01-01')
})

card_transactions_df = pd.DataFrame({
    'transaction_id': range(1, n_card_transactions + 1),
    'customer_id': card_customer_ids,
    'transaction_value': transaction_values,
    'category': categories,
    'is_fx_transaction': is_fx_transaction,
    'transaction_date': pd.date_range('2024-01-01', '2025-01-01', periods=n_card_transactions),
    'created_at': pd.Timestamp('2025-01-01')
})

loans_df = pd.DataFrame({
    'loan_id': range(1, n_loans + 1),
    'customer_id': loan_customer_ids,
    'loan_amount': loan_amounts,
    'loan_tenure_months': loan_tenures,
    'interest_rate': interest_rates,
    'loan_default': loan_defaults,
    'created_at': pd.Timestamp('2025-01-01'),
    'updated_at': pd.Timestamp('2025-01-01')
})

fx_transactions_df = pd.DataFrame({
    'fx_id': range(1, n_fx_transactions + 1),
    'customer_id': fx_customer_ids,
    'fx_volume_usd': fx_volume_usd,
    'transaction_date': pd.date_range('2024-01-01', '2025-01-01', periods=n_fx_transactions),
    'created_at': pd.Timestamp('2025-01-01')
})

# Save to CSVs
customers_df.to_csv(os.path.join(output_dir, "customers.csv"), index=False)
savings_accounts_df.to_csv(os.path.join(output_dir, "savings_accounts.csv"), index=False)
card_transactions_df.to_csv(os.path.join(output_dir, "card_transactions.csv"), index=False)
loans_df.to_csv(os.path.join(output_dir, "loans.csv"), index=False)
fx_transactions_df.to_csv(os.path.join(output_dir, "fx_transactions.csv"), index=False)

print(f"Mock NCBA datasets generated in {output_dir}:")
print(f"- customers.csv ({len(customers_df)} rows)")
print(f"- savings_accounts.csv ({len(savings_accounts_df)} rows)")
print(f"- card_transactions.csv ({len(card_transactions_df)} rows)")
print(f"- loans.csv ({len(loans_df)} rows)")
print(f"- fx_transactions.csv ({len(fx_transactions_df)} rows)")