from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Asset

User = get_user_model()


class PortfolioIntegrationTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_full_workflow(self):
        # 1. Ajouter un actif
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
        asset_id = response.data['id']
        
        # 2. Récupérer l'actif
        response = self.client.get(f'/api/portfolio/assets/{asset_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['symbol'], 'AAPL')
        
        # 3. Voir le résumé
        response = self.client.get('/api/portfolio/assets/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['asset_count'], 1)
        
        # 4. Mettre à jour l'actif
        update_data = {'current_price': Decimal('200')}
        response = self.client.patch(f'/api/portfolio/assets/{asset_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 5. Supprimer l'actif
        response = self.client.delete(f'/api/portfolio/assets/{asset_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 6. Vérifier que le portfolio est vide
        response = self.client.get('/api/portfolio/assets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class PortfolioSummaryTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Ajouter plusieurs actifs
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
        Asset.objects.create(
            user=self.user,
            asset_type='CRYPTO',
            symbol='BTC',
            name='Bitcoin',
            quantity=Decimal('0.5'),
            purchase_price=Decimal('40000'),
            current_price=Decimal('50000'),
            purchase_date='2024-01-01'
        )

    def test_portfolio_summary(self):
        response = self.client.get('/api/portfolio/assets/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['asset_count'], 2)
        self.assertIn('by_type', response.data)

    def test_portfolio_performance(self):
        response = self.client.get('/api/portfolio/assets/performance/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_assets'], 2)
        self.assertIsNotNone(response.data['best_performer'])
        self.assertIsNotNone(response.data['worst_performer'])
