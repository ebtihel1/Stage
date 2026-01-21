from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, PortfolioSummaryView, PortfolioPerformanceView

router = DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset')

urlpatterns = [
    path('', include(router.urls)),
    path('summary/', PortfolioSummaryView.as_view(), name='portfolio_summary'),
    path('performance/', PortfolioPerformanceView.as_view(), name='portfolio_performance'),
]
