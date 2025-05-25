from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, SavingsAccount, CardTransaction, Loan
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import logging
from decimal import Decimal
import pickle
import os
from sqlalchemy import create_engine
from django.db.utils import Error as dbError
from datetime import timedelta

# Define engine at module level
DATABASE_URL = 'postgresql://postgres:2003@db:5432/revenue'
engine = create_engine(DATABASE_URL)

logger = logging.getLogger(__name__)

class CustomerSegmentationView(APIView):
    def get(self, request):
        try:
            logger.info("Fetching customer data...")
            customers = Customer.objects.all().values(
                'customer_id', 'income', 'credit_score', 'is_diaspora'
            )
            savings = SavingsAccount.objects.all().values('customer_id', 'savings_balance', 'activity_score')
            card_transactions = CardTransaction.objects.values('customer_id').annotate(
                total_card_value=Sum('transaction_value'),
                transaction_count=Count('transaction_id')
            )
            loans = Loan.objects.values('customer_id').annotate(
                total_loan_amount=Sum('loan_amount'),
                avg_interest_rate=Sum('interest_rate') / Count('loan_id')
            )

            if not customers:
                logger.error("No customers found")
                return Response({"error": "No customers found"}, status=status.HTTP_404_NOT_FOUND)

            logger.info("Converting to DataFrames...")
            customers_df = pd.DataFrame(customers)
            savings_df = pd.DataFrame(savings)
            card_transactions_df = pd.DataFrame(card_transactions)
            loans_df = pd.DataFrame(loans)

            logger.info("Merging data...")
            data = customers_df.merge(savings_df, on='customer_id', how='left')
            data = data.merge(card_transactions_df, on='customer_id', how='left')
            data = data.merge(loans_df, on='customer_id', how='left')

            # Convert Decimal to float
            decimal_columns = ['total_card_value', 'total_loan_amount', 'avg_interest_rate']
            for col in decimal_columns:
                data[col] = data[col].apply(lambda x: float(x) if isinstance(x, Decimal) else x)

            # Fill missing values
            data['total_card_value'] = data['total_card_value'].fillna(0)
            data['savings_balance'] = data['savings_balance'].fillna(0)
            data['activity_score'] = data['activity_score'].fillna(0)
            data['transaction_count'] = data['transaction_count'].fillna(0)
            data['total_loan_amount'] = data['total_loan_amount'].fillna(0)
            data['avg_interest_rate'] = data['avg_interest_rate'].fillna(0)

            # Churn risk: Low activity_score (<0.3) or low transaction_count (<5)
            data['churn_risk'] = (data['activity_score'] < 0.3) | (data['transaction_count'] < 5)

            # Fee optimization (Linear Regression)
            fee_model = LinearRegression()
            X_fee = data[['income', 'savings_balance', 'total_card_value']].astype(float)
            y_fee = np.clip(X_fee.sum(axis=1) * 0.001, 100, 1000)  # Mock fee based on wealth
            fee_model.fit(X_fee, y_fee)
            data['recommended_fee'] = fee_model.predict(X_fee).round(2)

            features = ['income', 'credit_score', 'savings_balance', 'total_card_value', 'total_loan_amount']
            X = data[features].astype(float)

            if X.empty or len(X) < 3:
                logger.error(f"Insufficient data: {len(X)} rows")
                return Response({'error': 'Insufficient data'}, status=status.HTTP_400_BAD_REQUEST)

            logger.info("Standardizing features...")
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            k = min(3, len(X))
            logger.info(f"Running KMeans with k={k}...")
            kmeans = KMeans(n_clusters=k, random_state=42)
            data['cluster'] = kmeans.fit_predict(X_scaled)

            # Save clusters to customers table
            logger.info("Saving cluster assignments to database...")
            try:
                for _, row in data[['customer_id', 'cluster']].iterrows():
                    Customer.objects.filter(customer_id=row['customer_id']).update(cluster=row['cluster'])
            except dbError as e:
                logger.warning(f"Failed to save clusters: {str(e)}. Continuing without saving.")

            logger.info("Computing Elbow Method...")
            inertias = []
            for k in range(2, min(6, len(X) + 1)):
                kmeans = KMeans(n_clusters=k, random_state=42)
                kmeans.fit(X_scaled)
                inertias.append(kmeans.inertia_)

            logger.info("Summarizing clusters...")
            cluster_summary = data.groupby('cluster').agg({
                'income': 'mean',
                'credit_score': 'mean',
                'savings_balance': 'mean',
                'total_card_value': 'mean',
                'total_loan_amount': 'mean',
                'activity_score': 'mean',
                'churn_risk': 'mean',
                'recommended_fee': 'mean',
                'customer_id': 'count',
                'is_diaspora': 'sum'
            }).rename(columns={'customer_id': 'count', 'is_diaspora': 'diaspora_count'}).to_dict(orient='index')

            response = {
                'clusters': data[['customer_id', 'cluster']].to_dict(orient='records'),
                'summary': {
                    f'Cluster {i}': {
                        'avg_income': cluster_summary.get(i, {}).get('income', 0),
                        'avg_credit_score': cluster_summary.get(i, {}).get('credit_score', 0),
                        'avg_savings_balance': cluster_summary.get(i, {}).get('savings_balance', 0),
                        'avg_card_value': cluster_summary.get(i, {}).get('total_card_value', 0),
                        'avg_loan_amount': cluster_summary.get(i, {}).get('total_loan_amount', 0),
                        'avg_activity_score': cluster_summary.get(i, {}).get('activity_score', 0),
                        'churn_risk': cluster_summary.get(i, {}).get('churn_risk', 0),
                        'recommended_fee': cluster_summary.get(i, {}).get('recommended_fee', 0),
                        'count': cluster_summary.get(i, {}).get('count', 0),
                        'diaspora_count': cluster_summary.get(i, {}).get('diaspora_count', 0)
                    } for i in range(k)
                },
                'customers': data[['customer_id', 'income', 'credit_score', 'savings_balance', 'total_card_value', 'total_loan_amount', 'is_diaspora']].to_dict(orient='records'),
                'elbow': {'k': list(range(2, min(6, len(X) + 1))), 'inertia': inertias}
            }

            logger.info("Returning response")
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in segmentation: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoanRiskView(APIView):
    def get(self, request):
        try:
            logger.info("Fetching loan data for risk prediction...")
            query = """
            SELECT l.loan_id, l.customer_id, l.loan_amount, l.interest_rate, l.loan_tenure_months, 
                   c.income, c.credit_score, l.loan_default, c.cluster, s.activity_score,
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
            logger.info("Executing SQL query...")
            data = pd.read_sql(query, engine)
            logger.info(f"Retrieved {len(data)} rows")

            if data.empty:
                logger.error("No loan data found")
                return Response({'error': 'No loan data found'}, status=status.HTTP_404_NOT_FOUND)

            # Convert Decimal to float
            decimal_columns = ['loan_amount', 'interest_rate', 'total_card_value']
            for col in decimal_columns:
                data[col] = data[col].apply(lambda x: float(x) if isinstance(x, Decimal) else x)

            # Fill missing values
            data['activity_score'] = data['activity_score'].fillna(0)
            data['total_card_value'] = data['total_card_value'].fillna(0)
            data['cluster'] = data['cluster'].fillna(-1)
            data['age'] = data['age'].fillna(data['age'].median())
            data['segment'] = data['segment'].fillna('Unknown')

            # Encode categorical 'segment'
            logger.info("Encoding segment...")
            data = pd.get_dummies(data, columns=['segment'], prefix='segment')

            # Ensure all segment columns exist
            for col in ['segment_High Net Worth', 'segment_Low Income', 'segment_Middle Class']:
                if col not in data.columns:
                    data[col] = 0

            # Convert boolean to int
            data['is_diaspora'] = data['is_diaspora'].astype(int)

            # Load model and scaler
            model_path = '/app/models/loan_risk_model.pkl'
            scaler_path = '/app/models/scaler.pkl'
            logger.info(f"Loading model from {model_path} and scaler from {scaler_path}")
            if not os.path.exists(model_path) or not os.path.exists(scaler_path):
                logger.error("Model or scaler not found")
                return Response({'error': 'Model or scaler not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    scaler = pickle.load(f)
            except Exception as e:
                logger.error(f"Error loading model/scaler: {str(e)}")
                return Response({'error': f'Error loading model/scaler: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Prepare features
            features = ['loan_amount', 'interest_rate', 'loan_tenure_months', 'income', 'credit_score', 
                        'activity_score', 'total_card_value', 'is_diaspora', 'age', 
                        'segment_High Net Worth', 'segment_Low Income', 'segment_Middle Class']
            logger.info("Preparing features...")
            if not all(col in data.columns for col in features):
                missing_cols = [col for col in features if col not in data.columns]
                logger.error(f"Missing columns: {missing_cols}")
                return Response({'error': f'Missing columns: {missing_cols}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            X = data[features].astype(float)
            logger.info(f"Feature shape: {X.shape}")

            # Scale features
            try:
                X_scaled = scaler.transform(X)
            except Exception as e:
                logger.error(f"Error scaling features: {str(e)}")
                return Response({'error': f'Error scaling features: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Predict probabilities
            try:
                data['default_probability'] = model.predict_proba(X_scaled)[:, 1].round(3)
            except Exception as e:
                logger.error(f"Error predicting probabilities: {str(e)}")
                return Response({'error': f'Error predicting probabilities: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            data['risk_category'] = data['default_probability'].apply(
                lambda x: 'High' if x > 0.5 else 'Medium' if x > 0.2 else 'Low'
            )

            # Customer-level risk
            logger.info("Computing customer-level risk...")
            customer_risk = data.groupby('customer_id').agg({
                'default_probability': 'mean',
                'risk_category': 'first',
                'cluster': 'first'
            }).reset_index().rename(columns={'default_probability': 'avg_default_probability'})

            # Cluster-level risk
            logger.info("Computing cluster-level risk...")
            cluster_risk = data[data['cluster'] != -1].groupby('cluster').agg({
                'default_probability': 'mean',
                'loan_id': 'count',
                'loan_amount': 'mean',
                'credit_score': 'mean',
                'income': 'mean'
            }).reset_index().rename(columns={
                'default_probability': 'avg_default_probability',
                'loan_id': 'loan_count',
                'loan_amount': 'avg_loan_amount',
                'credit_score': 'avg_credit_score',
                'income': 'avg_income'
            })

            # Portfolio stats
            logger.info("Computing portfolio stats...")
            portfolio_stats = {
                'total_loans': len(data),
                'high_risk_loans': len(data[data['risk_category'] == 'High']),
                'medium_risk_loans': len(data[data['risk_category'] == 'Medium']),
                'low_risk_loans': len(data[data['risk_category'] == 'Low']),
                'avg_default_probability': data['default_probability'].mean().round(3)
            }

            # Fetch segmentation summary
            logger.info("Fetching segmentation summary...")
            try:
                seg_data = pd.DataFrame(Customer.objects.all().values('customer_id', 'cluster'))
                seg_summary = seg_data.groupby('cluster').agg({
                    'customer_id': 'count'
                }).rename(columns={'customer_id': 'customer_count'}).to_dict(orient='index')
                cluster_summary = {
                    f'Cluster {i}': {
                        'customer_count': seg_summary.get(i, {}).get('customer_count', 0)
                    } for i in range(3)
                }
            except Exception as e:
                logger.error(f"Error fetching segmentation summary: {str(e)}")
                cluster_summary = {}

            # Feature importance
            logger.info("Extracting feature importance...")
            try:
                if hasattr(model, 'feature_importances_'):
                    feature_importance = {feature: float(imp) for feature, imp in zip(features, model.feature_importances_)}
                elif hasattr(model, 'coef_'):
                    feature_importance = {feature: float(coef) for feature, coef in zip(features, model.coef_[0])}
                else:
                    feature_importance = {feature: 0.0 for feature in features}
                    logger.warning("Model has no feature importance attribute")
            except Exception as e:
                logger.error(f"Error extracting feature importance: {str(e)}")
                feature_importance = {feature: 0.0 for feature in features}

            response = {
                'loans': data[['loan_id', 'customer_id', 'loan_amount', 'default_probability', 'risk_category', 'cluster']].to_dict(orient='records'),
                'customers': customer_risk.to_dict(orient='records'),
                'clusters': cluster_risk.to_dict(orient='records'),
                'portfolio': portfolio_stats,
                'feature_importance': feature_importance,
                'cluster_summary': cluster_summary
            }

            logger.info("Returning loan risk response")
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in loan risk prediction: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FeeOptimizationView(APIView):
    def get(self, request):
        try:
            logger.info("Fetching data for fee optimization...")
            # Load customer data
            query = """
            SELECT c.customer_id, c.income, c.credit_score, c.is_diaspora, c.cluster,
                   COALESCE(s.savings_balance, 0) as savings_balance,
                   COALESCE(s.activity_score, 0) as activity_score,
                   COALESCE((
                       SELECT SUM(ct.transaction_value)
                       FROM card_transactions ct
                       WHERE ct.customer_id = c.customer_id
                   ), 0) as total_card_value
            FROM customers c
            LEFT JOIN savings_accounts s ON c.customer_id = s.customer_id
            """
            logger.info("Executing customer query...")
            data = pd.read_sql(query, engine)
            logger.info(f"Retrieved {len(data)} customer rows")

            if data.empty:
                logger.error("No customer data found")
                return Response({'error': 'No customer data found'}, status=status.HTTP_404_NOT_FOUND)

            # Load loan risk data
            logger.info("Computing loan risk probabilities...")
            loan_query = """
            SELECT l.loan_id, l.customer_id, l.loan_amount, l.interest_rate, l.loan_tenure_months,
                   c.income, c.credit_score, c.cluster, s.activity_score,
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
            loan_data = pd.read_sql(loan_query, engine)
            logger.info(f"Retrieved {len(loan_data)} loan rows")

            if not loan_data.empty:
                # Process loan data same as LoanRiskView
                # Convert Decimal to float
                decimal_columns = ['loan_amount', 'interest_rate', 'total_card_value']
                for col in decimal_columns:
                    loan_data[col] = loan_data[col].apply(lambda x: float(x) if isinstance(x, Decimal) else x)

                # Fill missing values
                loan_data['activity_score'] = loan_data['activity_score'].fillna(0)
                loan_data['total_card_value'] = loan_data['total_card_value'].fillna(0)
                loan_data['cluster'] = loan_data['cluster'].fillna(-1)
                loan_data['age'] = loan_data['age'].fillna(loan_data['age'].median())
                loan_data['segment'] = loan_data['segment'].fillna('Unknown')

                # Encode categorical 'segment'
                loan_data = pd.get_dummies(loan_data, columns=['segment'], prefix='segment')

                # Ensure all segment columns exist
                for col in ['segment_High Net Worth', 'segment_Low Income', 'segment_Middle Class']:
                    if col not in loan_data.columns:
                        loan_data[col] = 0

                loan_data['is_diaspora'] = loan_data['is_diaspora'].astype(int)

                # Load model and scaler
                model_path = '/app/models/loan_risk_model.pkl'
                scaler_path = '/app/models/scaler.pkl'
                if not os.path.exists(model_path) or not os.path.exists(scaler_path):
                    logger.error("Model or scaler not found")
                    return Response({'error': 'Model or scaler not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    scaler = pickle.load(f)

                # Prepare features
                features = ['loan_amount', 'interest_rate', 'loan_tenure_months', 'income', 'credit_score',
                            'activity_score', 'total_card_value', 'is_diaspora', 'age',
                            'segment_High Net Worth', 'segment_Low Income', 'segment_Middle Class']
                if not all(col in loan_data.columns for col in features):
                    missing_cols = [col for col in features if col not in loan_data.columns]
                    logger.error(f"Missing columns: {missing_cols}")
                    return Response({'error': f'Missing columns: {missing_cols}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                X = loan_data[features].astype(float)
                X_scaled = scaler.transform(X)
                loan_data['default_probability'] = model.predict_proba(X_scaled)[:, 1].round(3)

                # Aggregate to customer level
                loan_risk = loan_data.groupby('customer_id').agg({
                    'default_probability': 'mean'
                }).reset_index().rename(columns={'default_probability': 'avg_default_probability'})

                # Merge with customer data
                data = data.merge(loan_risk, on='customer_id', how='left')
            else:
                data['avg_default_probability'] = 0

            logger.info(f"Merged data shape: {data.shape}")

            # Convert Decimal to float
            decimal_columns = ['income', 'savings_balance', 'total_card_value']
            for col in decimal_columns:
                data[col] = data[col].apply(lambda x: float(x) if isinstance(x, Decimal) else x)

            # Fill missing values
            data['savings_balance'] = data['savings_balance'].fillna(0)
            data['total_card_value'] = data['total_card_value'].fillna(0)
            data['activity_score'] = data['activity_score'].fillna(0)
            data['avg_default_probability'] = data['avg_default_probability'].fillna(0)
            data['cluster'] = data['cluster'].fillna(-1)
            data['income'] = data['income'].fillna(data['income'].median())

            # Convert boolean to int
            data['is_diaspora'] = data['is_diaspora'].astype(int)

            # Calculate churn risk
            logger.info("Calculating churn risk...")
            data['churn_risk'] = (data['activity_score'] < 0.3).astype(int)

            # Calculate recommended fee
            def calculate_fee(row):
                try:
                    # Base fee: 0.1% of wealth (income + savings + card value)
                    wealth = row['income'] + row['savings_balance'] + row['total_card_value']
                    base_fee = wealth * 0.001  # 0.1%

                    # Risk adjustment
                    risk_multiplier = 1.2 if row['avg_default_probability'] > 0.5 else 1.1 if row['avg_default_probability'] > 0.2 else 1.0

                    # Cluster adjustment
                    cluster_multiplier = 0.8 if row['cluster'] == 0 else 1.2 if row['cluster'] == 2 else 1.0

                    # Apply adjustments
                    fee = base_fee * risk_multiplier * cluster_multiplier

                    # Cap fee to avoid churn
                    max_fee = row['income'] * 0.05 if row['churn_risk'] > 0.5 else row['income'] * 0.1
                    fee = min(fee, max_fee)

                    # Enforce min/max bounds
                    return max(100, min(fee, 1000))
                except Exception as e:
                    logger.error(f"Error calculating fee for customer {row['customer_id']}: {str(e)}")
                    return 100  # Default fee on error

            logger.info("Calculating recommended fees...")
            data['recommended_fee'] = data.apply(calculate_fee, axis=1).round(2)
            data['expected_revenue'] = data['recommended_fee'] * (1 - data['churn_risk'] * 0.5)  # Adjust for churn likelihood

            # Customer-level summary
            customer_fees = data[['customer_id', 'cluster', 'recommended_fee', 'expected_revenue', 'churn_risk', 'avg_default_probability']].copy()

            # Cluster-level summary
            logger.info("Computing cluster-level summary...")
            cluster_fees = data[data['cluster'] != -1].groupby('cluster').agg({
                'recommended_fee': 'mean',
                'expected_revenue': 'sum',
                'churn_risk': 'mean',
                'customer_id': 'count',
                'avg_default_probability': 'mean'
            }).reset_index().rename(columns={
                'recommended_fee': 'avg_recommended_fee',
                'expected_revenue': 'total_revenue',
                'churn_risk': 'avg_churn_risk',
                'customer_id': 'customer_count',
                'avg_default_probability': 'avg_default_probability'
            })

            # Portfolio stats
            logger.info("Computing portfolio stats...")
            portfolio_stats = {
                'total_customers': len(data),
                'total_revenue': data['expected_revenue'].sum().round(2),
                'avg_recommended_fee': data['recommended_fee'].mean().round(2),
                'avg_churn_risk': data['churn_risk'].mean().round(3)
            }

            response = {
                'customers': customer_fees.to_dict(orient='records'),
                'clusters': cluster_fees.to_dict(orient='records'),
                'portfolio': portfolio_stats
            }

            logger.info("Returning fee optimization response")
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in fee optimization: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
