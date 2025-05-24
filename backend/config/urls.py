from django.urls import path
from engine.views import CustomerSegmentationView

urlpatterns = [
    path('api/segmentation/', CustomerSegmentationView.as_view(), name='customer-segmentation'),
]