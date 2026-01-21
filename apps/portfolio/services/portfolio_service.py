"""
Portfolio Service - Logique métier pour la gestion du portefeuille
Utilise Dependency Injection pour les dépendances
"""

from typing import Dict, List, Any
from decimal import Decimal
from .interfaces import IAssetRepository, IPerformanceCalculator
from .calculators import SimpleROICalculator
from ..models import Asset


class PortfolioService:
    """
    Service pour la gestion du portefeuille.
    Implémente la Dependency Injection pour faciliter les tests.
    """

    def __init__(
        self,
        asset_repository: IAssetRepository,
        calculator: IPerformanceCalculator = None
    ):
        """
        Initialiser le service avec ses dépendances
        
        Args:
            asset_repository: Repository pour accéder aux actifs
            calculator: Calculator pour calculer la performance (par défaut SimpleROICalculator)
        """
        self.asset_repository = asset_repository
        self.calculator = calculator or SimpleROICalculator()

    def get_user_assets(self, user_id: int) -> List[Asset]:
        """
        Récupérer tous les actifs d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des actifs
        """
        return self.asset_repository.find_all_by_user(user_id)

    def get_asset_detail(self, user_id: int, asset_id: int) -> Asset:
        """
        Récupérer les détails d'un actif
        
        Args:
            user_id: ID de l'utilisateur (pour vérifier l'ownership)
            asset_id: ID de l'actif
            
        Returns:
            Asset
            
        Raises:
            Asset.DoesNotExist
        """
        asset = self.asset_repository.find_by_id(asset_id)
        if not asset or asset.user_id != user_id:
            raise Asset.DoesNotExist("Actif non trouvé")
        return asset

    def create_asset(self, user_id: int, asset_data: Dict[str, Any]) -> Asset:
        """
        Créer un nouvel actif
        
        Args:
            user_id: ID de l'utilisateur propriétaire
            asset_data: Données de l'actif
            
        Returns:
            Asset créé
        """
        return self.asset_repository.create(user_id, asset_data)

    def update_asset(
        self,
        user_id: int,
        asset_id: int,
        asset_data: Dict[str, Any]
    ) -> Asset:
        """
        Mettre à jour un actif
        
        Args:
            user_id: ID de l'utilisateur (vérification ownership)
            asset_id: ID de l'actif
            asset_data: Données à mettre à jour
            
        Returns:
            Asset mis à jour
            
        Raises:
            Asset.DoesNotExist
        """
        asset = self.get_asset_detail(user_id, asset_id)
        return self.asset_repository.update(asset_id, asset_data)

    def delete_asset(self, user_id: int, asset_id: int) -> bool:
        """
        Supprimer un actif
        
        Args:
            user_id: ID de l'utilisateur (vérification ownership)
            asset_id: ID de l'actif à supprimer
            
        Returns:
            True si suppression réussie
            
        Raises:
            Asset.DoesNotExist
        """
        self.get_asset_detail(user_id, asset_id)
        return self.asset_repository.delete(asset_id)

    def get_portfolio_summary(self, user_id: int) -> Dict[str, Any]:
        """
        Obtenir un résumé du portefeuille avec les totaux
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict contenant les informations du portefeuille
        """
        assets = self.get_user_assets(user_id)
        
        total_current_value = sum(asset.current_value for asset in assets)
        total_purchase_value = sum(asset.purchase_value for asset in assets)
        total_gain_loss = total_current_value - total_purchase_value
        
        if total_purchase_value > 0:
            overall_performance = (total_gain_loss / total_purchase_value) * 100
        else:
            overall_performance = 0.0

        # Grouper par type d'actif
        by_type = {}
        for asset in assets:
            asset_type = asset.get_asset_type_display()
            if asset_type not in by_type:
                by_type[asset_type] = {
                    'count': 0,
                    'value': 0.0,
                    'assets': []
                }
            by_type[asset_type]['count'] += 1
            by_type[asset_type]['value'] += asset.current_value
            by_type[asset_type]['assets'].append({
                'id': asset.id,
                'symbol': asset.symbol,
                'name': asset.name,
                'quantity': str(asset.quantity),
                'current_price': str(asset.current_price),
                'current_value': asset.current_value,
            })

        return {
            'total_current_value': total_current_value,
            'total_purchase_value': total_purchase_value,
            'total_gain_loss': total_gain_loss,
            'overall_performance_percentage': round(overall_performance, 2),
            'asset_count': len(assets),
            'by_type': by_type
        }

    def get_portfolio_performance(self, user_id: int) -> Dict[str, Any]:
        """
        Obtenir la performance globale du portefeuille
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict contenant les métriques de performance
        """
        assets = self.get_user_assets(user_id)
        
        if not assets:
            return {
                'total_assets': 0,
                'average_performance': 0.0,
                'best_performer': None,
                'worst_performer': None,
                'assets': []
            }

        performances = [
            {
                'symbol': asset.symbol,
                'name': asset.name,
                'performance': self.calculator.calculate(asset),
                'gain_loss': asset.gain_loss,
            }
            for asset in assets
        ]

        performances.sort(key=lambda x: x['performance'], reverse=True)

        avg_performance = sum(p['performance'] for p in performances) / len(performances)

        return {
            'total_assets': len(assets),
            'average_performance': round(avg_performance, 2),
            'best_performer': performances[0] if performances else None,
            'worst_performer': performances[-1] if performances else None,
            'assets': performances
        }
