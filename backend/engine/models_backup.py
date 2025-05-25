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
    customer = models.ForeignKey('Customer', on_delete=models.RESTRICT)
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
    customer = models.ForeignKey('Customer', on_delete=models.RESTRICT)
    savings_balance = models.IntegerField(validators=[MinValueValidator(0)])
    monthly_deposit = models.IntegerField(validators=[MinValueValidator(0)])
    activity_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'savings_accounts'

class FxTransaction(models.Model):
    fx_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('Customer', on_delete=models.RESTRICT, to_field='customer_id', db_column='customer_id', related_name='fx_transactions')
    fx_volume_usd = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    currency_pair = models.CharField(max_length=7, null=True)
    bid_rate = models.DecimalField(max_digits=10, decimal_places=4, validators=[MinValueValidator(0)], null=True)
    ask_rate = models.DecimalField(max_digits=10, decimal_places=4, validators=[MinValueValidator(0)], null=True)
    transaction_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'fx_transactions'

class CardTransaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('Customer', on_delete=models.RESTRICT)
    transaction_value = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    category = models.CharField(max_length=50)
    is_fx_transaction = models.BooleanField(default=False)
    transaction_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'card_transactions'