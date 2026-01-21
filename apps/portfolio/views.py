from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from .models import Asset
from .serializers import (
    AssetSerializer,
    AssetCreateUpdateSerializer,
    PortfolioSummarySerializer,
    PerformanceSerializer
)
from .services.portfolio_service import PortfolioService
from .services.repositories import DjangoAssetRepository
from .services.calculators import SimpleROICalculator


class AssetViewSet(ModelViewSet):
    """
    ViewSet pour la gestion des actifs
    Endpoints:
    - GET /api/portfolio/assets/ - Lister tous les actifs de l'utilisateur
    - POST /api/portfolio/assets/ - Créer un nouvel actif
    - GET /api/portfolio/assets/{id}/ - Récupérer les détails d'un actif
    - PUT /api/portfolio/assets/{id}/ - Mettre à jour un actif
    - DELETE /api/portfolio/assets/{id}/ - Supprimer un actif
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Ne retourner que les actifs de l'utilisateur connecté"""
        return Asset.objects.filter(user=self.request.user).order_by('-created_at')

    def get_serializer_class(self):
        """Utiliser des serializers différents selon l'action"""
        if self.action in ['create', 'update', 'partial_update']:
            return AssetCreateUpdateSerializer
        return AssetSerializer

    def perform_create(self, serializer):
        """Créer un actif associé à l'utilisateur connecté"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Mettre à jour un actif"""
        serializer.save()

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Endpoint personnalisé pour le résumé du portefeuille
        GET /api/portfolio/assets/summary/
        """
        service = PortfolioService(
            asset_repository=DjangoAssetRepository(),
            calculator=SimpleROICalculator()
        )
        
        summary = service.get_portfolio_summary(request.user.id)
        serializer = PortfolioSummarySerializer(summary)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def performance(self, request):
        """
        Endpoint personnalisé pour la performance du portefeuille
        GET /api/portfolio/assets/performance/
        """
        service = PortfolioService(
            asset_repository=DjangoAssetRepository(),
            calculator=SimpleROICalculator()
        )
        
        performance = service.get_portfolio_performance(request.user.id)
        serializer = PerformanceSerializer(performance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PortfolioSummaryView(generics.GenericAPIView):
    """
    Vue pour obtenir le résumé du portefeuille
    GET /api/portfolio/summary/
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = PortfolioSummarySerializer

    def get(self, request, *args, **kwargs):
        """Récupérer le résumé du portefeuille"""
        service = PortfolioService(
            asset_repository=DjangoAssetRepository(),
            calculator=SimpleROICalculator()
        )
        
        summary = service.get_portfolio_summary(request.user.id)
        serializer = self.get_serializer(summary)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PortfolioPerformanceView(generics.GenericAPIView):
    """
    Vue pour obtenir la performance du portefeuille
    GET /api/portfolio/performance/
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = PerformanceSerializer

    def get(self, request, *args, **kwargs):
        """Récupérer la performance du portefeuille"""
        service = PortfolioService(
            asset_repository=DjangoAssetRepository(),
            calculator=SimpleROICalculator()
        )
        
        performance = service.get_portfolio_performance(request.user.id)
        serializer = self.get_serializer(performance)
        return Response(serializer.data, status=status.HTTP_200_OK)
