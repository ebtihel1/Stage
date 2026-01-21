"""
Interfaces pour implémenter les Design Patterns (Strategy, Repository)
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from decimal import Decimal


class IPerformanceCalculator(ABC):
    """Interface Strategy Pattern pour les calculs de performance"""

    @abstractmethod
    def calculate(self, asset: 'Asset') -> float:
        """Calculer la performance d'un actif"""
        pass


class IAssetRepository(ABC):
    """Interface Repository Pattern pour l'accès aux données Asset"""

    @abstractmethod
    def find_by_id(self, asset_id: int) -> Optional['Asset']:
        """Trouver un actif par ID"""
        pass

    @abstractmethod
    def find_all_by_user(self, user_id: int) -> List['Asset']:
        """Récupérer tous les actifs d'un utilisateur"""
        pass

    @abstractmethod
    def create(self, user_id: int, asset_data: Dict[str, Any]) -> 'Asset':
        """Créer un nouvel actif"""
        pass

    @abstractmethod
    def update(self, asset_id: int, asset_data: Dict[str, Any]) -> 'Asset':
        """Mettre à jour un actif"""
        pass

    @abstractmethod
    def delete(self, asset_id: int) -> bool:
        """Supprimer un actif"""
        pass

    @abstractmethod
    def sum_by_type(self, user_id: int) -> Dict[str, Decimal]:
        """Obtenir la somme des actifs par type pour un utilisateur"""
        pass
