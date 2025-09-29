"""
Tests for CFO functions - no API calls required.
These tests verify that the core financial calculation functions work correctly.
"""

import pytest
from agent import cfo_functions


class TestRevenueVsBudget:
    """Tests for get_revenue_vs_budget function."""
    
    def test_returns_correct_structure(self):
        """Test that function returns all required fields."""
        result = cfo_functions.get_revenue_vs_budget(1, 2025, 1, 2025)
        
        assert isinstance(result, dict)
        assert 'actual_usd' in result
        assert 'budget_usd' in result
        assert 'difference' in result
        assert 'percent_diff' in result
        
    def test_values_are_numeric(self):
        """Test that all returned values are numbers."""
        result = cfo_functions.get_revenue_vs_budget(1, 2025, 1, 2025)
        
        assert isinstance(result['actual_usd'], (int, float))
        assert isinstance(result['budget_usd'], (int, float))
        assert isinstance(result['difference'], (int, float))
        assert isinstance(result['percent_diff'], (int, float))
    
    def test_difference_calculation(self):
        """Test that difference is calculated correctly."""
        result = cfo_functions.get_revenue_vs_budget(1, 2025, 1, 2025)
        
        expected_diff = result['actual_usd'] - result['budget_usd']
        assert abs(result['difference'] - expected_diff) < 0.01
    
    def test_percent_calculation(self):
        """Test that percentage is calculated correctly."""
        result = cfo_functions.get_revenue_vs_budget(1, 2025, 1, 2025)
        
        if result['budget_usd'] != 0:
            expected_pct = (result['difference'] / result['budget_usd']) * 100
            assert abs(result['percent_diff'] - expected_pct) < 0.01


class TestGrossMargin:
    """Tests for gross margin functions."""
    
    def test_margin_trend_returns_dict(self):
        """Test that calculate_gross_margin returns a dictionary."""
        result = cfo_functions.calculate_gross_margin(1, 2025, 3, 2025)
        
        assert isinstance(result, dict)
        assert len(result) > 0
    
    def test_margin_values_are_numeric(self):
        """Test that margin percentages are numbers."""
        result = cfo_functions.calculate_gross_margin(1, 2025, 1, 2025)
        
        for month, margin in result.items():
            assert isinstance(margin, (int, float))
            assert -100 <= margin <= 200  # Reasonable margin range
    
    def test_aggregate_margin_structure(self):
        """Test that aggregate margin returns correct structure."""
        result = cfo_functions.calculate_gross_margin_aggregate(1, 2025, 3, 2025)
        
        assert isinstance(result, dict)
        assert 'margin_percent' in result
        assert 'total_revenue' in result
        assert 'total_cogs' in result
    
    def test_aggregate_margin_calculation(self):
        """Test that aggregate margin is calculated correctly."""
        result = cfo_functions.calculate_gross_margin_aggregate(1, 2025, 1, 2025)
        
        gross_profit = result['total_revenue'] - result['total_cogs']
        if result['total_revenue'] != 0:
            expected_margin = (gross_profit / result['total_revenue']) * 100
            assert abs(result['margin_percent'] - expected_margin) < 0.1


class TestOpex:
    """Tests for operating expense functions."""
    
    def test_returns_categories(self):
        """Test that opex_by_category returns expense categories."""
        result = cfo_functions.opex_by_category(1, 2025, 3, 2025)
        
        assert isinstance(result, dict)
        assert len(result) > 0
    
    def test_category_values_are_numeric(self):
        """Test that expense amounts are numbers."""
        result = cfo_functions.opex_by_category(1, 2025, 3, 2025)
        
        for category, amount in result.items():
            assert isinstance(category, str)
            assert isinstance(amount, (int, float))
            assert amount >= 0  # Expenses should be positive


class TestCashRunway:
    """Tests for cash runway function."""
    
    def test_returns_correct_structure(self):
        """Test that cash runway returns all required fields."""
        result = cfo_functions.calculate_cash_runway(1, 2025, 3, 2025)
        
        assert isinstance(result, dict)
        assert 'current_cash' in result
        assert 'monthly_cash_flow' in result
        assert 'runway_months' in result
    
    def test_values_are_numeric(self):
        """Test that runway values are numbers."""
        result = cfo_functions.calculate_cash_runway(1, 2025, 3, 2025)
        
        assert isinstance(result['current_cash'], (int, float))
        assert isinstance(result['monthly_cash_flow'], (int, float))
        assert isinstance(result['runway_months'], (int, float))
    
    def test_runway_calculation_logic(self):
        """Test that runway is calculated correctly."""
        result = cfo_functions.calculate_cash_runway(1, 2025, 3, 2025)
        
        if result['monthly_cash_flow'] < 0:
            # Negative cash flow means burning cash
            expected_runway = result['current_cash'] / abs(result['monthly_cash_flow'])
            assert abs(result['runway_months'] - expected_runway) < 0.01
        else:
            # Positive cash flow means infinite runway
            assert result['runway_months'] == float('inf')


class TestEBITDA:
    """Tests for EBITDA function."""
    
    def test_returns_correct_structure(self):
        """Test that EBITDA returns all required fields."""
        result = cfo_functions.calculate_ebitda(1, 2025, 3, 2025)
        
        assert isinstance(result, dict)
        assert 'ebitda_usd' in result
        assert 'total_revenue' in result
        assert 'total_cogs' in result
        assert 'total_opex' in result
    
    def test_ebitda_calculation(self):
        """Test that EBITDA is calculated correctly."""
        result = cfo_functions.calculate_ebitda(1, 2025, 1, 2025)
        
        expected_ebitda = (result['total_revenue'] - 
                          result['total_cogs'] - 
                          result['total_opex'])
        
        assert abs(result['ebitda_usd'] - expected_ebitda) < 0.01


class TestCurrencyConversion:
    """Tests for currency conversion functions."""
    
    def test_usd_conversion_returns_same(self):
        """Test that USD amounts are returned unchanged."""
        from agent.data_loader import load_data
        _, _, _, fx = load_data()
        
        # USD to USD should be 1:1
        result = cfo_functions.convert_to_usd(100, 'USD', '2025-01', fx)
        assert result == 100.0
    
    def test_conversion_returns_float(self):
        """Test that conversion always returns a float."""
        from agent.data_loader import load_data
        _, _, _, fx = load_data()
        
        result = cfo_functions.convert_to_usd(100, 'USD', '2025-01', fx)
        assert isinstance(result, float)