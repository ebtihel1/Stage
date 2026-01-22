from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from ..models import Asset

User = get_user_model()


class AssetCreateTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_stock_asset(self):
        data = {
            'asset_type': 'STOCK',
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'quantity': Decimal('10'),
            'purchase_price': Decimal('150.50'),
            'current_price': Decimal('175.25'),
            'purchase_date': '2024-01-15'
        }
        response = self.client.post('/api/portfolio/assets/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['symbol'], 'AAPL')
        self.assertEqual(float(response.data['quantity']), 10.0)

    def test_create_bond_asset(self):
        data = {
            'asset_type': 'BOND',
            'symbol': 'US10Y',
            'name': '10-Year US Treasury Bond',
            'quantity': Decimal('5'),
            'purchase_price': Decimal('100'),
            'current_price': Decimal('102'),
            'purchase_date': '2024-01-10'
        }
        response = self.client.post('/api/portfolio/assets/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['asset_type'], 'BOND')

    def test_create_crypto_asset(self):
        data = {
            'asset_type': 'CRYPTO',
            'symbol': 'BTC',
            'name': 'Bitcoin',
            'quantity': Decimal('0.5'),
            'purchase_price': Decimal('45000'),
            'current_price': Decimal('50000'),
            'purchase_date': '2024-01-01'
        }
        response = self.client.post('/api/portfolio/assets/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['symbol'], 'BTC')

    def test_create_asset_invalid_quantity(self):
        data = {
            'asset_type': 'STOCK',
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'quantity': Decimal('-10'),
            'purchase_price': Decimal('150.50'),
            'current_price': Decimal('175.25'),
            'purchase_date': '2024-01-15'
        }
        response = self.client.post('/api/portfolio/assets/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_asset_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            'asset_type': 'STOCK',
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'quantity': Decimal('10'),
            'purchase_price': Decimal('150.50'),
            'current_price': Decimal('175.25'),
            'purchase_date': '2024-01-15'
        }
        response = self.client.post('/api/portfolio/assets/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AssetListTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        Asset.objects.create(
            user=self.user,
            asset_type='STOCK',
            symbol='AAPL',
            name='Apple Inc.',
            quantity=Decimal('10'),
            purchase_price=Decimal('150.50'),
            current_price=Decimal('175.25'),
            purchase_date='2024-01-15'
        )
        Asset.objects.create(
            user=self.other_user,
            asset_type='STOCK',
            symbol='MSFT',
            name='Microsoft',
            quantity=Decimal('5'),
            purchase_price=Decimal('300'),
            current_price=Decimal('350'),
            purchase_date='2024-01-15'
        )
        
        self.client.force_authenticate(user=self.user)

    def test_list_user_assets(self):
        response = self.client.get('/api/portfolio/assets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['symbol'], 'AAPL')

    def test_list_does_not_show_other_users_assets(self):
        response = self.client.get('/api/portfolio/assets/')
        symbols = [asset['symbol'] for asset in response.data]
        self.assertNotIn('MSFT', symbols)


class AssetDetailTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.asset = Asset.objects.create(
            user=self.user,
            asset_type='STOCK',
            symbol='AAPL',
            name='Apple Inc.',
            quantity=Decimal('10'),
            purchase_price=Decimal('150.50'),
            current_price=Decimal('175.25'),
            purchase_date='2024-01-15'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_asset_detail(self):
        response = self.client.get(f'/api/portfolio/assets/{self.asset.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['symbol'], 'AAPL')

    def test_update_asset(self):
        data = {
            'current_price': Decimal('200')
        }
        response = self.client.patch(f'/api/portfolio/assets/{self.asset.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.current_price, Decimal('200'))

    def test_delete_asset(self):
        response = self.client.delete(f'/api/portfolio/assets/{self.asset.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Asset.objects.filter(id=self.asset.id).exists())


class AssetPropertiesTests(APITestCase):
    
    def test_current_value_calculation(self):
        asset = Asset(
            user=None,
            asset_type='STOCK',
            symbol='AAPL',
            name='Apple',
            quantity=Decimal('10'),
            purchase_price=Decimal('100'),
            current_price=Decimal('150'),
            purchase_date='2024-01-15'
        )
        self.assertEqual(asset.current_value, 1500.0)

    def test_gain_loss_calculation(self):
        asset = Asset(
            user=None,
            asset_type='STOCK',
            symbol='AAPL',
            name='Apple',
            quantity=Decimal('10'),
            purchase_price=Decimal('100'),
            current_price=Decimal('150'),
            purchase_date='2024-01-15'
        )
        self.assertEqual(asset.gain_loss, 500.0)

    def test_performance_percentage_calculation(self):
        asset = Asset(
            user=None,
            asset_type='STOCK',
            symbol='AAPL',
            name='Apple',
            quantity=Decimal('10'),
            purchase_price=Decimal('100'),
            current_price=Decimal('150'),
            purchase_date='2024-01-15'
        )
        self.assertEqual(asset.performance_percentage, 50.0)

    def test_performance_percentage_loss(self):
        asset = Asset(
            user=None,
            asset_type='STOCK',
            symbol='AAPL',
            name='Apple',
            quantity=Decimal('10'),
            purchase_price=Decimal('100'),
            current_price=Decimal('80'),
            purchase_date='2024-01-15'
        )
        self.assertEqual(asset.performance_percentage, -20.0)
