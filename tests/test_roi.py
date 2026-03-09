from api.calculators.roi import calculate_roi
import pytest

def test_basic_roi():
    result = calculate_roi(initial_investment=1000, final_value=1500, years=1.0)
    assert result["roi_percent"] == pytest.approx(50.0, rel=1e-3)
    assert result["profit_loss"] == pytest.approx(500.0, rel=1e-3)

def test_annualized_roi():
    result = calculate_roi(initial_investment=1000, final_value=1500, years=2.0)
    assert result["annualized_roi_percent"] == pytest.approx(22.47, rel=1e-2)

def test_negative_roi():
    result = calculate_roi(initial_investment=1000, final_value=800, years=1.0)
    assert result["roi_percent"] == pytest.approx(-20.0, rel=1e-3)
    assert result["profit_loss"] == pytest.approx(-200.0, rel=1e-3)
