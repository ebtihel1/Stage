"""
Strategy Pattern - Calculators pour différents algorithmes de performance
"""

from .interfaces import IPerformanceCalculator


class SimpleROICalculator(IPerformanceCalculator):
    """
    Calcul du ROI simple (Return On Investment)
    ROI = ((Valeur actuelle - Valeur achetée) / Valeur achetée) * 100
    """

    def calculate(self, asset) -> float:
        """
        Calcule le ROI en pourcentage
        
        Args:
            asset: Objet Asset
            
        Returns:
            float: Pourcentage du ROI
        """
        current_value = float(asset.quantity * asset.current_price)
        purchase_value = float(asset.quantity * asset.purchase_price)
        
        if purchase_value == 0:
            return 0.0
        
        return ((current_value - purchase_value) / purchase_value) * 100


class AbsoluteGainCalculator(IPerformanceCalculator):
    """Calcul du gain/perte en valeur absolue"""

    def calculate(self, asset) -> float:
        """
        Calcule le gain ou perte en montant absolu
        
        Args:
            asset: Objet Asset
            
        Returns:
            float: Montant du gain/perte
        """
        current_value = float(asset.quantity * asset.current_price)
        purchase_value = float(asset.quantity * asset.purchase_price)
        return current_value - purchase_value


class AnnualizedReturnCalculator(IPerformanceCalculator):
    """Calcul du retour annualisé"""

    def calculate(self, asset) -> float:
        """
        Calcule le retour annualisé basé sur la date d'achat
        
        Args:
            asset: Objet Asset
            
        Returns:
            float: Retour annualisé en pourcentage
        """
        from datetime import datetime
        
        purchase_value = float(asset.quantity * asset.purchase_price)
        if purchase_value == 0:
            return 0.0
        
        current_value = float(asset.quantity * asset.current_price)
        roi = (current_value - purchase_value) / purchase_value
        
        # Calculer le nombre de jours
        days = (datetime.now().date() - asset.purchase_date).days
        if days == 0:
            return 0.0
        
        # Convertir en années (365 jours)
        years = days / 365.0
        
        # Retour annualisé
        annualized = ((1 + roi) ** (1 / years)) - 1
        return annualized * 100
