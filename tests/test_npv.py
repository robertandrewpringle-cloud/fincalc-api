from api.calculators.npv import calculate_npv
import pytest

def test_profitable_project():
    cash_flows = [-1000, 400, 400, 400]
    result = calculate_npv(rate=10.0, cash_flows=cash_flows)
    assert result["npv"] == pytest.approx(-5.26, abs=0.1)
    assert result["is_profitable"] == False

def test_clearly_profitable():
    cash_flows = [-1000, 500, 500, 500]
    result = calculate_npv(rate=10.0, cash_flows=cash_flows)
    assert result["npv"] > 0
    assert result["is_profitable"] == True

def test_zero_rate():
    cash_flows = [-1000, 400, 400, 400]
    result = calculate_npv(rate=0.0, cash_flows=cash_flows)
    assert result["npv"] == pytest.approx(200.0, rel=1e-3)
