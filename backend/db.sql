CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    age INTEGER CHECK (age >= 0 AND age <= 120), -- Constrain age to realistic values
    income INTEGER CHECK (income >= 0), -- Ensure non-negative income
    credit_score INTEGER CHECK (credit_score >= 300 AND credit_score <= 850), -- Typical credit score range
    is_diaspora BOOLEAN NOT NULL DEFAULT FALSE, -- Explicitly require value
    segment VARCHAR(50) NOT NULL, -- Prevent null segments
    preferred_currency CHAR(3) NOT NULL, -- ISO 4217 currency code (e.g., GBP, USD)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Track record creation
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Track record updates
    CONSTRAINT valid_segment CHECK (segment IN ('Low Income', 'Middle Class', 'High Net Worth')) -- Example segments
);

CREATE TABLE loans (
    loan_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    loan_amount INTEGER CHECK (loan_amount > 0), -- Ensure positive loan amounts
    loan_tenure_months INTEGER CHECK (loan_tenure_months > 0), -- Ensure valid tenure
    interest_rate DECIMAL(5,2) CHECK (interest_rate >= 0), -- Non-negative interest rate
    loan_default BOOLEAN NOT NULL DEFAULT FALSE, -- Explicitly require value
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE savings_accounts (
    account_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    savings_balance INTEGER CHECK (savings_balance >= 0), -- Non-negative balance
    monthly_deposit INTEGER CHECK (monthly_deposit >= 0), -- Non-negative deposits
    activity_score FLOAT CHECK (activity_score >= 0 AND activity_score <= 1), -- Constrain to [0,1] range
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fx_transactions (
    fx_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    fx_volume_usd DECIMAL(12,2) CHECK (fx_volume_usd >= 0), -- Support larger USD volumes
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Track transaction time
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE card_transactions (
    transaction_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    transaction_value DECIMAL(12,2) CHECK (transaction_value >= 0),
    category VARCHAR(50) NOT NULL,
    is_fx_transaction BOOLEAN NOT NULL DEFAULT FALSE,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);