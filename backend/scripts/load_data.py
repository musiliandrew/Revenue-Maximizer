import pandas as pd
from sqlalchemy import create_engine, text
import os

# Database connection
engine = create_engine('postgresql://revenue_maximizer_db_user:fNO9hsvh0loMBnwECf7TbVMwhxPj7kBD@dpg-d0pmn63e5dus73e0gtdg-a.oregon-postgres.render.com/revenue_maximizer_db')


# Input directory
input_dir = os.path.join(os.path.dirname(__file__), '..', 'data')


# Load CSVs
customers_df = pd.read_csv(os.path.join(input_dir, "customers.csv"))
savings_accounts_df = pd.read_csv(os.path.join(input_dir, "savings_accounts.csv"))
card_transactions_df = pd.read_csv(os.path.join(input_dir, "card_transactions.csv"))
loans_df = pd.read_csv(os.path.join(input_dir, "loans.csv"))
fx_transactions_df = pd.read_csv(os.path.join(input_dir, "fx_transactions.csv"))

# Ensure correct data types
customers_df['is_diaspora'] = customers_df['is_diaspora'].astype(bool)
savings_accounts_df['activity_score'] = savings_accounts_df['activity_score'].astype(float)
card_transactions_df['transaction_value'] = card_transactions_df['transaction_value'].astype(float)
card_transactions_df['is_fx_transaction'] = card_transactions_df['is_fx_transaction'].astype(bool)
loans_df['interest_rate'] = loans_df['interest_rate'].astype(float)
loans_df['loan_default'] = loans_df['loan_default'].astype(bool)
fx_transactions_df['fx_volume_usd'] = fx_transactions_df['fx_volume_usd'].astype(float)

# Convert dates to datetime
for df in [customers_df, savings_accounts_df, card_transactions_df, loans_df, fx_transactions_df]:
    df['created_at'] = pd.to_datetime(df['created_at'])
    if 'updated_at' in df.columns:
        df['updated_at'] = pd.to_datetime(df['updated_at'])
    if 'transaction_date' in df.columns:
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])

# Drop dependent tables with CASCADE
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS card_transactions CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS fx_transactions CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS loans CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS savings_accounts CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS customers CASCADE;"))
    conn.commit()

# Save to database
customers_df.to_sql('customers', engine, if_exists='replace', index=False)
savings_accounts_df.to_sql('savings_accounts', engine, if_exists='replace', index=False)
card_transactions_df.to_sql('card_transactions', engine, if_exists='replace', index=False)
loans_df.to_sql('loans', engine, if_exists='replace', index=False)
fx_transactions_df.to_sql('fx_transactions', engine, if_exists='replace', index=False)

print("Data loaded successfully into PostgreSQL:")
print(f"- customers: {len(customers_df)} rows")
print(f"- savings_accounts: {len(savings_accounts_df)} rows")
print(f"- card_transactions: {len(card_transactions_df)} rows")
print(f"- loans: {len(loans_df)} rows")
print(f"- fx_transactions: {len(fx_transactions_df)} rows")