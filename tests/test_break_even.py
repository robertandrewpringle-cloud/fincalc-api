from api.calculators.break_even import calculate_break_even
import pytest

def test_basic_break_even():
    result = calculate_break_even(fixed_costs=10_000, variable_cost_per_unit=5.0, price_per_unit=15.0)
    assert result["break_even_units"] == pytest.approx(1000.0, rel=1e-3)
    assert result["break_even_revenue"] == pytest.approx(15_000.0, rel=1e-3)

def test_contribution_margin():
    result = calculate_break_even(fixed_costs=10_000, variable_cost_per_unit=5.0, price_per_unit=15.0)
    assert result["contribution_margin"] == pytest.approx(10.0, rel=1e-3)
    assert result["contribution_margin_ratio"] == pytest.approx(0.6667, rel=1e-2)

def test_price_below_variable_cost_raises():
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        calculate_break_even(fixed_costs=10_000, variable_cost_per_unit=20.0, price_per_unit=15.0)
