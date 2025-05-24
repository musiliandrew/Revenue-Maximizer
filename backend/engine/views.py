from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, SavingsAccount, CardTransaction
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class CustomerSegmentationView(APIView):
    def get(self, request):
        try:
            # Fetch data
            customers = Customer.objects.all().values('customer_id', 'income', 'credit_score')
            savings = SavingsAccount.objects.all().values('customer_id', 'savings_balance')
            card_transactions = CardTransaction.objects.values('customer_id').annotate(
                total_card_value=Sum('transaction_value')
            )

            # Convert to DataFrames
            customers_df = pd.DataFrame(customers)
            savings_df = pd.DataFrame(savings)
            card_transactions_df = pd.DataFrame(card_transactions)

            # Merge data
            data = customers_df.merge(savings_df, on='customer_id', how='left')
            data = data.merge(card_transactions_df, on='customer_id', how='left')

            # Fill missing values (e.g., customers with no card transactions)
            data['total_card_value'] = data['total_card_value'].fillna(0)

            # Select features for clustering
            features = ['income', 'credit_score', 'savings_balance', 'total_card_value']
            X = data[features]

            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Run KMeans
            k = 3  # Number of clusters (can tune with Elbow Method)
            kmeans = KMeans(n_clusters=k, random_state=42)
            data['cluster'] = kmeans.fit_predict(X_scaled)

            # Summarize clusters
            cluster_summary = data.groupby('cluster')[features].mean().to_dict()

            # Prepare response
            response = {
                'clusters': data[['customer_id', 'cluster']].to_dict(orient='records'),
                'summary': {
                    f'Cluster {i}': {
                        'avg_income': cluster_summary['income'][i],
                        'avg_credit_score': cluster_summary['credit_score'][i],
                        'avg_savings_balance': cluster_summary['savings_balance'][i],
                        'avg_card_value': cluster_summary['total_card_value'][i]
                    } for i in range(k)
                }
            }

            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)