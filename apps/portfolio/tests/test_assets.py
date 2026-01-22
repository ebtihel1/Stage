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


class AssetDuplicateTests(APITestCase):
    """Tests pour vérifier la validation des doublons"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_duplicate_asset_same_user(self):
        # Créer le premier actif
        data1 = {
            'asset_type': 'STOCK',
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'quantity': Decimal('10'),
            'purchase_price': Decimal('150.50'),
            'current_price': Decimal('175.25'),
            'purchase_date': '2024-01-15'
        }
        response1 = self.client.post('/api/portfolio/assets/', data1)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Tenter de créer le même actif
        response2 = self.client.post('/api/portfolio/assets/', data1)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_different_symbol_same_date_allowed(self):
        data1 = {
            'asset_type': 'STOCK',
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'quantity': Decimal('10'),
            'purchase_price': Decimal('150.50'),
            'current_price': Decimal('175.25'),
            'purchase_date': '2024-01-15'
        }
        response1 = self.client.post('/api/portfolio/assets/', data1)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Créer avec un autre symbole à la même date
        data2 = {
            'asset_type': 'STOCK',
            'symbol': 'MSFT',
            'name': 'Microsoft',
            'quantity': Decimal('5'),
            'purchase_price': Decimal('300'),
            'current_price': Decimal('350'),
            'purchase_date': '2024-01-15'
        }
        response2 = self.client.post('/api/portfolio/assets/', data2)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

    def test_create_same_symbol_different_date_allowed(self):
        data1 = {
            'asset_type': 'STOCK',
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'quantity': Decimal('10'),
            'purchase_price': Decimal('150.50'),
            'current_price': Decimal('175.25'),
            'purchase_date': '2024-01-15'
        }
        response1 = self.client.post('/api/portfolio/assets/', data1)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Créer le même symbole à une date différente
        data2 = {
            'asset_type': 'STOCK',
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'quantity': Decimal('5'),
            'purchase_price': Decimal('160'),
            'current_price': Decimal('180'),
            'purchase_date': '2024-01-20'
        }
        response2 = self.client.post('/api/portfolio/assets/', data2)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)


class AssetValidationTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_with_zero_price_values(self):
        data = {
            'asset_type': 'STOCK',
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'quantity': Decimal('10'),
            'purchase_price': Decimal('0'),
            'current_price': Decimal('175.25'),
            'purchase_date': '2024-01-15'
        }
        response = self.client.post('/api/portfolio/assets/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_negative_current_price(self):
        data = {
            'asset_type': 'STOCK',
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'quantity': Decimal('10'),
            'purchase_price': Decimal('150'),
            'current_price': Decimal('-175'),
            'purchase_date': '2024-01-15'
        }
        response = self.client.post('/api/portfolio/assets/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_zero_quantity(self):
        data = {
            'asset_type': 'STOCK',
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'quantity': Decimal('0'),
            'purchase_price': Decimal('150'),
            'current_price': Decimal('175'),
            'purchase_date': '2024-01-15'
        }
        response = self.client.post('/api/portfolio/assets/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_required_field(self):
        data = {
            'asset_type': 'STOCK',
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'quantity': Decimal('10'),
            # missing purchase_price
            'current_price': Decimal('175.25'),
            'purchase_date': '2024-01-15'
        }
        response = self.client.post('/api/portfolio/assets/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AssetUpdateTests(APITestCase):
    
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

    def test_update_current_price_only(self):
        data = {'current_price': Decimal('200')}
        response = self.client.patch(f'/api/portfolio/assets/{self.asset.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.current_price, Decimal('200'))

    def test_full_update_asset(self):
        data = {
            'asset_type': 'STOCK',
            'symbol': 'AAPL',
            'name': 'Apple Inc. Updated',
            'quantity': Decimal('20'),
            'purchase_price': Decimal('160'),
            'current_price': Decimal('200'),
            'purchase_date': '2024-01-15'
        }
        response = self.client.put(f'/api/portfolio/assets/{self.asset.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.quantity, Decimal('20'))

    def test_update_nonexistent_asset(self):
        data = {'current_price': Decimal('200')}
        response = self.client.patch('/api/portfolio/assets/9999/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PortfolioSummaryTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_summary_endpoint(self):
        Asset.objects.create(
            user=self.user,
            asset_type='STOCK',
            symbol='AAPL',
            name='Apple',
            quantity=Decimal('10'),
            purchase_price=Decimal('100'),
            current_price=Decimal('150'),
            purchase_date='2024-01-15'
        )
        response = self.client.get('/api/portfolio/assets/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_current_value', response.data)
        self.assertIn('total_purchase_value', response.data)


class PortfolioPerformanceTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_performance_endpoint(self):
        Asset.objects.create(
            user=self.user,
            asset_type='STOCK',
            symbol='AAPL',
            name='Apple',
            quantity=Decimal('10'),
            purchase_price=Decimal('100'),
            current_price=Decimal('150'),
            purchase_date='2024-01-15'
        )
        response = self.client.get('/api/portfolio/assets/performance/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_assets', response.data)
        self.assertIn('average_performance', response.data)
