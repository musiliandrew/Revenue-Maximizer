from django.urls import path
from . import views

urlpatterns = [
    path('segmentation/', views.CustomerSegmentationView.as_view(), name='segmentation'),
    path('loan-risk/', views.LoanRiskView.as_view(), name='loan-risk'),
    path('fee-optimization/', views.FeeOptimizationView.as_view(), name='fee-optimization'),
]