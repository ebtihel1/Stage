from rest_framework import serializers
from .models import Asset


class AssetSerializer(serializers.ModelSerializer):
    """Serializer pour les opérations CRUD sur les actifs"""
    
    current_value = serializers.SerializerMethodField()
    gain_loss = serializers.SerializerMethodField()
    performance_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = [
            'id',
            'asset_type',
            'symbol',
            'name',
            'quantity',
            'purchase_price',
            'current_price',
            'purchase_date',
            'current_value',
            'gain_loss',
            'performance_percentage',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'current_value', 'gain_loss', 'performance_percentage']

    def get_current_value(self, obj):
        return round(obj.current_value, 2)

    def get_gain_loss(self, obj):
        return round(obj.gain_loss, 2)

    def get_performance_percentage(self, obj):
        return round(obj.performance_percentage, 2)


class AssetCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier les actifs"""

    class Meta:
        model = Asset
        fields = [
            'asset_type',
            'symbol',
            'name',
            'quantity',
            'purchase_price',
            'current_price',
            'purchase_date',
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être positive")
        return value

    def validate_purchase_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le prix d'achat doit être positif")
        return value

    def validate_current_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le prix actuel doit être positif")
        return value


class PortfolioSummarySerializer(serializers.Serializer):
    """Serializer pour le résumé du portefeuille"""
    
    total_current_value = serializers.FloatField()
    total_purchase_value = serializers.FloatField()
    total_gain_loss = serializers.FloatField()
    overall_performance_percentage = serializers.FloatField()
    asset_count = serializers.IntegerField()
    by_type = serializers.DictField()


class PerformanceSerializer(serializers.Serializer):
    """Serializer pour la performance du portefeuille"""
    
    total_assets = serializers.IntegerField()
    average_performance = serializers.FloatField()
    best_performer = serializers.DictField(required=False, allow_null=True)
    worst_performer = serializers.DictField(required=False, allow_null=True)
    assets = serializers.ListField()
