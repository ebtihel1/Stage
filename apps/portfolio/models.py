from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Asset(models.Model):
    """Modèle pour représenter un actif (Stock, Obligation, Crypto)"""
    
    class AssetType(models.TextChoices):
        STOCK = 'STOCK', 'Action'
        BOND = 'BOND', 'Obligation'
        CRYPTO = 'CRYPTO', 'Crypto-monnaie'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assets')
    asset_type = models.CharField(
        max_length=10,
        choices=AssetType.choices,
        verbose_name="Type d'actif"
    )
    symbol = models.CharField(
        max_length=10,
        verbose_name="Symbole"
    )  # Ex: AAPL, BTC
    name = models.CharField(
        max_length=100,
        verbose_name="Nom de l'actif"
    )
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        verbose_name="Quantité"
    )
    purchase_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name="Prix d'achat"
    )
    current_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name="Prix actuel"
    )
    purchase_date = models.DateField(
        verbose_name="Date d'achat"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de mise à jour"
    )

    class Meta:
        verbose_name = "Actif"
        verbose_name_plural = "Actifs"
        ordering = ['-created_at']
        unique_together = ('user', 'symbol', 'purchase_date')

    def __str__(self):
        return f"{self.symbol} - {self.name} ({self.get_asset_type_display()})"

    @property
    def current_value(self) -> float:
        """Valeur actuelle du portefeuille pour cet actif"""
        return float(self.quantity * self.current_price)

    @property
    def purchase_value(self) -> float:
        """Valeur d'achat initiale"""
        return float(self.quantity * self.purchase_price)

    @property
    def gain_loss(self) -> float:
        """Gain ou perte en valeur absolue"""
        return self.current_value - self.purchase_value

    @property
    def performance_percentage(self) -> float:
        """Performance en pourcentage"""
        if self.purchase_value == 0:
            return 0.0
        return (self.gain_loss / self.purchase_value) * 100
