from api.calculators.mortgage import calculate_mortgage
import pytest

def test_basic_mortgage():
    result = calculate_mortgage(home_price=300_000, down_payment=60_000,
                                annual_rate=6.5, term_years=30)
    assert result["loan_amount"] == pytest.approx(240_000.0, rel=1e-3)
    assert result["monthly_payment"] == pytest.approx(1517.47, rel=1e-3)

def test_total_cost():
    result = calculate_mortgage(home_price=300_000, down_payment=60_000,
                                annual_rate=6.5, term_years=30)
    assert result["total_payment"] == pytest.approx(546_289.20, rel=1e-2)
    assert result["total_interest"] > result["loan_amount"]

def test_down_payment_percentage():
    result = calculate_mortgage(home_price=300_000, down_payment=60_000,
                                annual_rate=6.5, term_years=30)
    assert result["down_payment_percent"] == pytest.approx(20.0, rel=1e-3)
