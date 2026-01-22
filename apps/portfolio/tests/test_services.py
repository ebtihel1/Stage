from django.test import TestCase
from decimal import Decimal
from ..models import Asset
from ..services.calculators import (
    SimpleROICalculator,
    AbsoluteGainCalculator,
    AnnualizedReturnCalculator
)
from ..services.repositories import DjangoAssetRepository
from ..services.portfolio_service import PortfolioService
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

User = get_user_model()


class SimpleROICalculatorTests(TestCase):
    
    def test_roi_positive(self):
        asset = Asset(
            asset_type='STOCK',
            symbol='AAPL',
            name='Apple',
            quantity=Decimal('10'),
            purchase_price=Decimal('100'),
            current_price=Decimal('150'),
            purchase_date='2024-01-15'
        )
        calculator = SimpleROICalculator()
        roi = calculator.calculate(asset)
        self.assertEqual(roi, 50.0)

    def test_roi_negative(self):
        asset = Asset(
            asset_type='STOCK',
            symbol='AAPL',
            name='Apple',
            quantity=Decimal('10'),
            purchase_price=Decimal('100'),
            current_price=Decimal('80'),
            purchase_date='2024-01-15'
        )
        calculator = SimpleROICalculator()
        roi = calculator.calculate(asset)
        self.assertEqual(roi, -20.0)

    def test_roi_zero_purchase_price(self):
        asset = Asset(
            asset_type='STOCK',
            symbol='AAPL',
            name='Apple',
            quantity=Decimal('0'),
            purchase_price=Decimal('0'),
            current_price=Decimal('150'),
            purchase_date='2024-01-15'
        )
        calculator = SimpleROICalculator()
        roi = calculator.calculate(asset)
        self.assertEqual(roi, 0.0)


class AbsoluteGainCalculatorTests(TestCase):
    
    def test_absolute_gain_positive(self):
        asset = Asset(
            asset_type='STOCK',
            symbol='AAPL',
            name='Apple',
            quantity=Decimal('10'),
            purchase_price=Decimal('100'),
            current_price=Decimal('150'),
            purchase_date='2024-01-15'
        )
        calculator = AbsoluteGainCalculator()
        gain = calculator.calculate(asset)
        self.assertEqual(gain, 500.0)

    def test_absolute_gain_negative(self):
        asset = Asset(
            asset_type='STOCK',
            symbol='AAPL',
            name='Apple',
            quantity=Decimal('10'),
            purchase_price=Decimal('100'),
            current_price=Decimal('80'),
            purchase_date='2024-01-15'
        )
        calculator = AbsoluteGainCalculator()
        gain = calculator.calculate(asset)
        self.assertEqual(gain, -200.0)


class RepositoryTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.repository = DjangoAssetRepository()
        
        self.asset1 = Asset.objects.create(
            user=self.user,
            asset_type='STOCK',
            symbol='AAPL',
            name='Apple',
            quantity=Decimal('10'),
            purchase_price=Decimal('100'),
            current_price=Decimal('150'),
            purchase_date='2024-01-15'
        )
        self.asset2 = Asset.objects.create(
            user=self.user,
            asset_type='CRYPTO',
            symbol='BTC',
            name='Bitcoin',
            quantity=Decimal('0.5'),
            purchase_price=Decimal('40000'),
            current_price=Decimal('50000'),
            purchase_date='2024-01-10'
        )

    def test_find_by_id(self):
        asset = self.repository.find_by_id(self.asset1.id)
        self.assertIsNotNone(asset)
        self.assertEqual(asset.symbol, 'AAPL')

    def test_find_by_id_not_found(self):
        asset = self.repository.find_by_id(9999)
        self.assertIsNone(asset)

    def test_find_all_by_user(self):
        assets = self.repository.find_all_by_user(self.user.id)
        self.assertEqual(len(assets), 2)

    def test_create_asset(self):
        data = {
            'asset_type': 'BOND',
            'symbol': 'US10Y',
            'name': 'US Treasury',
            'quantity': Decimal('5'),
            'purchase_price': Decimal('100'),
            'current_price': Decimal('102'),
            'purchase_date': '2024-01-20'
        }
        asset = self.repository.create(self.user.id, data)
        self.assertIsNotNone(asset.id)
        self.assertEqual(asset.symbol, 'US10Y')

    def test_update_asset(self):
        data = {'current_price': Decimal('200')}
        asset = self.repository.update(self.asset1.id, data)
        self.assertEqual(asset.current_price, Decimal('200'))

    def test_delete_asset(self):
        result = self.repository.delete(self.asset1.id)
        self.assertTrue(result)
        self.assertIsNone(self.repository.find_by_id(self.asset1.id))

    def test_sum_by_type(self):
        summary = self.repository.sum_by_type(self.user.id)
        self.assertIn('STOCK', summary)
        self.assertIn('CRYPTO', summary)


class PortfolioServiceTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.service = PortfolioService(
            asset_repository=DjangoAssetRepository(),
            calculator=SimpleROICalculator()
        )
        
        self.asset1 = Asset.objects.create(
            user=self.user,
            asset_type='STOCK',
            symbol='AAPL',
            name='Apple',
            quantity=Decimal('10'),
            purchase_price=Decimal('100'),
            current_price=Decimal('150'),
            purchase_date='2024-01-15'
        )
        self.asset2 = Asset.objects.create(
            user=self.user,
            asset_type='STOCK',
            symbol='MSFT',
            name='Microsoft',
            quantity=Decimal('5'),
            purchase_price=Decimal('200'),
            current_price=Decimal('220'),
            purchase_date='2024-01-10'
        )

    def test_get_user_assets(self):
        assets = self.service.get_user_assets(self.user.id)
        self.assertEqual(len(assets), 2)

    def test_get_portfolio_summary(self):
        summary = self.service.get_portfolio_summary(self.user.id)
        self.assertIn('total_current_value', summary)
        self.assertIn('total_purchase_value', summary)
        self.assertIn('total_gain_loss', summary)
        self.assertIn('overall_performance_percentage', summary)
        self.assertEqual(summary['asset_count'], 2)

    def test_portfolio_summary_values(self):
        summary = self.service.get_portfolio_summary(self.user.id)
        expected_current = (10 * 150) + (5 * 220)
        expected_purchase = (10 * 100) + (5 * 200)
        self.assertEqual(summary['total_current_value'], expected_current)
        self.assertEqual(summary['total_purchase_value'], expected_purchase)

    def test_get_portfolio_performance(self):
        performance = self.service.get_portfolio_performance(self.user.id)
        self.assertIn('total_assets', performance)
        self.assertIn('average_performance', performance)
        self.assertIn('best_performer', performance)
        self.assertIn('worst_performer', performance)
        self.assertEqual(performance['total_assets'], 2)

    def test_create_asset(self):
        data = {
            'asset_type': 'CRYPTO',
            'symbol': 'ETH',
            'name': 'Ethereum',
            'quantity': Decimal('2'),
            'purchase_price': Decimal('2000'),
            'current_price': Decimal('2500'),
            'purchase_date': '2024-01-20'
        }
        asset = self.service.create_asset(self.user.id, data)
        self.assertIsNotNone(asset.id)
        self.assertEqual(asset.symbol, 'ETH')

    def test_delete_asset(self):
        result = self.service.delete_asset(self.user.id, self.asset1.id)
        self.assertTrue(result)
        assets = self.service.get_user_assets(self.user.id)
        self.assertEqual(len(assets), 1)

    def test_empty_portfolio(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        summary = self.service.get_portfolio_summary(other_user.id)
        self.assertEqual(summary['asset_count'], 0)
        self.assertEqual(summary['total_current_value'], 0)
