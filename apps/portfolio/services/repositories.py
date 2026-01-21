"""
Repository Pattern - Abstraction de l'accès aux données
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from django.db.models import Sum
from ..models import Asset
from .interfaces import IAssetRepository


class DjangoAssetRepository(IAssetRepository):
    """
    Implémentation du Repository Pattern pour les modèles Asset Django.
    Centralise la logique d'accès aux données et facilite les tests.
    """

    def find_by_id(self, asset_id: int) -> Optional[Asset]:
        """
        Trouver un actif par ID
        
        Args:
            asset_id: ID de l'actif
            
        Returns:
            Asset ou None
        """
        try:
            return Asset.objects.get(id=asset_id)
        except Asset.DoesNotExist:
            return None

    def find_all_by_user(self, user_id: int) -> List[Asset]:
        """
        Récupérer tous les actifs d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des actifs de l'utilisateur
        """
        return Asset.objects.filter(user_id=user_id).order_by('-created_at')

    def create(self, user_id: int, asset_data: Dict[str, Any]) -> Asset:
        """
        Créer un nouvel actif
        
        Args:
            user_id: ID de l'utilisateur propriétaire
            asset_data: Données de l'actif
            
        Returns:
            Asset créé
        """
        return Asset.objects.create(user_id=user_id, **asset_data)

    def update(self, asset_id: int, asset_data: Dict[str, Any]) -> Asset:
        """
        Mettre à jour un actif
        
        Args:
            asset_id: ID de l'actif à mettre à jour
            asset_data: Nouvelles données
            
        Returns:
            Asset mis à jour
            
        Raises:
            Asset.DoesNotExist
        """
        asset = Asset.objects.get(id=asset_id)
        for key, value in asset_data.items():
            setattr(asset, key, value)
        asset.save()
        return asset

    def delete(self, asset_id: int) -> bool:
        """
        Supprimer un actif
        
        Args:
            asset_id: ID de l'actif à supprimer
            
        Returns:
            True si suppression réussie, False sinon
        """
        try:
            Asset.objects.get(id=asset_id).delete()
            return True
        except Asset.DoesNotExist:
            return False

    def sum_by_type(self, user_id: int) -> Dict[str, Decimal]:
        """
        Obtenir la somme des valeurs actuelles par type d'actif
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict avec les sommes par type (STOCK, BOND, CRYPTO)
        """
        result = Asset.objects.filter(user_id=user_id).values('asset_type').annotate(
            total_value=Sum('current_price')
        )
        
        return {
            item['asset_type']: item['total_value'] or Decimal(0)
            for item in result
        }

    def find_by_user_and_symbol(self, user_id: int, symbol: str) -> List[Asset]:
        """
        Trouver les actifs d'un utilisateur par symbole
        
        Args:
            user_id: ID de l'utilisateur
            symbol: Symbole de l'actif (ex: AAPL)
            
        Returns:
            Liste des actifs correspondants
        """
        return Asset.objects.filter(
            user_id=user_id,
            symbol=symbol
        ).order_by('-created_at')

    def get_portfolio_value(self, user_id: int) -> Decimal:
        """
        Obtenir la valeur totale du portefeuille d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Valeur totale en montant décimal
        """
        total = Asset.objects.filter(user_id=user_id).aggregate(
            total=Sum('current_price')
        )
        return total['total'] or Decimal(0)

    def get_portfolio_purchase_value(self, user_id: int) -> Decimal:
        """
        Obtenir la valeur d'achat totale du portefeuille
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Valeur d'achat totale
        """
        total = Asset.objects.filter(user_id=user_id).aggregate(
            total=Sum('purchase_price')
        )
        return total['total'] or Decimal(0)
