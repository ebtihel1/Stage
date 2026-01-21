"""
Factory Pattern - Création de différents types d'actifs
"""

from typing import Dict, Callable, Any
from ..models import Asset


class AssetFactory:
    """
    Factory Pattern pour créer différents types d'actifs de manière flexible.
    Permet l'ajout facile de nouveaux types d'actifs sans modifier le code existant.
    """

    _creators: Dict[str, Callable] = {}

    @classmethod
    def register(cls, asset_type: str, creator: Callable) -> None:
        """
        Enregistrer un nouveau créateur pour un type d'actif
        
        Args:
            asset_type: Type d'actif (STOCK, BOND, CRYPTO)
            creator: Fonction ou classe qui crée l'actif
        """
        cls._creators[asset_type] = creator

    @classmethod
    def create(cls, asset_type: str, **kwargs) -> Asset:
        """
        Créer un actif du type spécifié
        
        Args:
            asset_type: Type d'actif à créer
            **kwargs: Paramètres pour la création de l'actif
            
        Returns:
            Asset: L'actif créé
            
        Raises:
            ValueError: Si le type d'actif n'est pas enregistré
        """
        creator = cls._creators.get(asset_type)
        if creator is None:
            raise ValueError(f"Type d'actif '{asset_type}' non enregistré")
        return creator(**kwargs)

    @classmethod
    def get_available_types(cls) -> list:
        """Retourner les types d'actifs disponibles"""
        return list(cls._creators.keys())


# Créateurs par défaut pour chaque type d'actif
def create_stock(user_id: int, **kwargs) -> Asset:
    """Créer un actif de type Action"""
    return Asset.objects.create(
        user_id=user_id,
        asset_type=Asset.AssetType.STOCK,
        **kwargs
    )


def create_bond(user_id: int, **kwargs) -> Asset:
    """Créer un actif de type Obligation"""
    return Asset.objects.create(
        user_id=user_id,
        asset_type=Asset.AssetType.BOND,
        **kwargs
    )


def create_crypto(user_id: int, **kwargs) -> Asset:
    """Créer un actif de type Crypto-monnaie"""
    return Asset.objects.create(
        user_id=user_id,
        asset_type=Asset.AssetType.CRYPTO,
        **kwargs
    )


# Enregistrer les créateurs
AssetFactory.register(Asset.AssetType.STOCK, create_stock)
AssetFactory.register(Asset.AssetType.BOND, create_bond)
AssetFactory.register(Asset.AssetType.CRYPTO, create_crypto)
