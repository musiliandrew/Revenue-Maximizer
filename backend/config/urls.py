from django.urls import path, include
from engine.views import health_check

urlpatterns = [
    path('api/', include('engine.urls')),
    path('health/', health_check, name='health'),
]