from django.test import TestCase
from decimal import Decimal
from ..models import Asset
from ..services.asset_factory import AssetFactory
from django.contrib.auth import get_user_model

User = get_user_model()


class AssetFactoryTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_stock(self):
        asset = AssetFactory.create(
            'STOCK',
            user_id=self.user.id,
            symbol='AAPL',
            name='Apple Inc.',
            quantity=Decimal('10'),
            purchase_price=Decimal('150'),
            current_price=Decimal('175'),
            purchase_date='2024-01-15'
        )
        self.assertEqual(asset.asset_type, 'STOCK')
        self.assertEqual(asset.symbol, 'AAPL')

    def test_create_bond(self):
        asset = AssetFactory.create(
            'BOND',
            user_id=self.user.id,
            symbol='US10Y',
            name='US Treasury',
            quantity=Decimal('5'),
            purchase_price=Decimal('100'),
            current_price=Decimal('102'),
            purchase_date='2024-01-10'
        )
        self.assertEqual(asset.asset_type, 'BOND')
        self.assertEqual(asset.symbol, 'US10Y')

    def test_create_crypto(self):
        asset = AssetFactory.create(
            'CRYPTO',
            user_id=self.user.id,
            symbol='BTC',
            name='Bitcoin',
            quantity=Decimal('0.5'),
            purchase_price=Decimal('40000'),
            current_price=Decimal('50000'),
            purchase_date='2024-01-01'
        )
        self.assertEqual(asset.asset_type, 'CRYPTO')
        self.assertEqual(asset.symbol, 'BTC')

    def test_create_invalid_type(self):
        with self.assertRaises(ValueError):
            AssetFactory.create(
                'INVALID_TYPE',
                user_id=self.user.id,
                symbol='XXX',
                name='Invalid',
                quantity=Decimal('1'),
                purchase_price=Decimal('100'),
                current_price=Decimal('100'),
                purchase_date='2024-01-01'
            )

    def test_get_available_types(self):
        types = AssetFactory.get_available_types()
        self.assertIn('STOCK', types)
        self.assertIn('BOND', types)
        self.assertIn('CRYPTO', types)

    def test_register_new_creator(self):
        def create_custom_asset(user_id, **kwargs):
            return Asset.objects.create(
                user_id=user_id,
                asset_type='STOCK',
                **kwargs
            )
        
        AssetFactory.register('CUSTOM', create_custom_asset)
        self.assertIn('CUSTOM', AssetFactory.get_available_types())

    def test_factory_with_all_required_fields(self):
        asset = AssetFactory.create(
            'STOCK',
            user_id=self.user.id,
            symbol='GOOGL',
            name='Google',
            quantity=Decimal('5'),
            purchase_price=Decimal('100'),
            current_price=Decimal('120'),
            purchase_date='2024-01-01'
        )
        self.assertIsNotNone(asset.id)
        self.assertEqual(asset.symbol, 'GOOGL')
        self.assertEqual(asset.name, 'Google')
        self.assertEqual(asset.quantity, Decimal('5'))

    def test_factory_creates_with_decimal_quantity(self):
        asset = AssetFactory.create(
            'CRYPTO',
            user_id=self.user.id,
            symbol='ETH',
            name='Ethereum',
            quantity=Decimal('0.5'),
            purchase_price=Decimal('2000'),
            current_price=Decimal('2500'),
            purchase_date='2024-01-01'
        )
        self.assertEqual(asset.quantity, Decimal('0.5'))

    def test_factory_case_sensitive(self):
        with self.assertRaises(ValueError):
            AssetFactory.create(
                'stock',  # lowercase, should fail
                user_id=self.user.id,
                symbol='AAPL',
                name='Apple',
                quantity=Decimal('1'),
                purchase_price=Decimal('100'),
                current_price=Decimal('100'),
                purchase_date='2024-01-01'
            )
