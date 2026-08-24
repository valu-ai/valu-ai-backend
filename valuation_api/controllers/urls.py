from django.urls import path
from valuation_api.controllers.views import (
    PropertyValuationEstimateView,
    PropertyValuationListView,
    PropertyValuationDetailView,
    PropertyDistrictsListView,
)

urlpatterns = [
    path('districts/', PropertyDistrictsListView.as_view(), name='valuation-districts'),
    path('estimate/', PropertyValuationEstimateView.as_view(), name='valuation-estimate'),
    path('', PropertyValuationListView.as_view(), name='valuation-list'),
    path('<int:pk>/', PropertyValuationDetailView.as_view(), name='valuation-detail'),
]