from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(120)])
    income = models.IntegerField(validators=[MinValueValidator(0)])
    credit_score = models.FloatField(validators=[MinValueValidator(300), MaxValueValidator(850)])
    is_diaspora = models.BooleanField(default=False)
    cluster = models.IntegerField(null=True, blank=True)
    segment = models.CharField(max_length=50)
    preferred_currency = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'customers'

class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    loan_amount = models.IntegerField(validators=[MinValueValidator(1)])
    loan_tenure_months = models.IntegerField(validators=[MinValueValidator(1)])
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    loan_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'loans'

class SavingsAccount(models.Model):
    account_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    savings_balance = models.IntegerField(validators=[MinValueValidator(0)])
    monthly_deposit = models.IntegerField(validators=[MinValueValidator(0)])
    activity_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'savings_accounts'

class CardTransaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, to_field='customer_id', db_column='customer_id')
    transaction_value = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    category = models.CharField(max_length=50)
    is_fx_transaction = models.BooleanField(default=False)
    transaction_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'card_transactions'