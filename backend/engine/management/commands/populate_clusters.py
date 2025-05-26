from django.core.management.base import BaseCommand
from django.db import transaction
from rest_framework.response import Response
from engine.views import CustomerSegmentationView
import logging
import pandas as pd
from engine.models import Customer

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Populates the cluster column in the customers table using segmentation logic'

    def handle(self, *args, **kwargs):
        self.stdout.write('Running customer segmentation to populate clusters...')
        try:
            # Simulate a GET request
            request = type('Request', (), {'method': 'GET'})()
            response = CustomerSegmentationView().get(request)

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Failed to populate clusters: {response.data}'))
                return

            # Extract clusters from response
            clusters = response.data.get('clusters', [])
            if not clusters:
                self.stdout.write(self.style.ERROR('No clusters found in response'))
                return

            # Convert to DataFrame
            df = pd.DataFrame(clusters)

            # Update clusters in bulk
            self.stdout.write('Updating clusters in database...')
            with transaction.atomic():
                # Clear existing clusters to avoid duplicates
                Customer.objects.all().update(cluster=None)

                # Create a dictionary for updates
                cluster_map = {row['customer_id']: row['cluster'] for row in clusters}

                # Bulk update
                for customer in Customer.objects.filter(customer_id__in=cluster_map.keys()):
                    customer.cluster = cluster_map[customer.customer_id]
                    customer.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully populated {len(clusters)} clusters'))

        except Exception as e:
            logger.error(f'Error in populate_clusters: {str(e)}', exc_info=True)
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))