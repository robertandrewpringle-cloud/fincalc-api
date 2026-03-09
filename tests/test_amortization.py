from api.calculators.amortization import calculate_amortization
import pytest

def test_basic_amortization():
    result = calculate_amortization(principal=100_000, annual_rate=5.0, term_months=12)
    assert result["monthly_payment"] == pytest.approx(8560.75, rel=1e-3)
    assert result["total_payment"] == pytest.approx(102729.0, rel=1e-3)
    assert len(result["schedule"]) == 12

def test_schedule_first_month():
    result = calculate_amortization(principal=100_000, annual_rate=5.0, term_months=12)
    first = result["schedule"][0]
    assert first["month"] == 1
    assert first["interest"] == pytest.approx(416.67, rel=1e-3)
    assert first["balance"] < 100_000

def test_final_balance_near_zero():
    result = calculate_amortization(principal=100_000, annual_rate=5.0, term_months=12)
    last = result["schedule"][-1]
    assert last["balance"] == pytest.approx(0.0, abs=0.01)
