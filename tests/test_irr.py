from api.calculators.irr import calculate_irr
import pytest

def test_basic_irr():
    cash_flows = [-1000, 1100]
    result = calculate_irr(cash_flows=cash_flows)
    assert result["irr_percent"] == pytest.approx(10.0, rel=1e-3)

def test_multi_period_irr():
    cash_flows = [-1000, 300, 400, 500]
    result = calculate_irr(cash_flows=cash_flows)
    assert result["irr_percent"] == pytest.approx(8.90, rel=1e-2)

def test_irr_no_solution_raises():
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        calculate_irr(cash_flows=[100, 200, 300])
