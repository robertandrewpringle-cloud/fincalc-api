from api.calculators.compound_interest import calculate_compound_interest
import pytest

def test_annual_compounding():
    result = calculate_compound_interest(principal=1000, annual_rate=10.0, years=5, compounds_per_year=1)
    assert result["final_amount"] == pytest.approx(1610.51, rel=1e-3)
    assert result["total_interest"] == pytest.approx(610.51, rel=1e-3)

def test_monthly_compounding():
    result = calculate_compound_interest(principal=1000, annual_rate=10.0, years=5, compounds_per_year=12)
    assert result["final_amount"] == pytest.approx(1645.31, rel=1e-3)

def test_growth_factor():
    result = calculate_compound_interest(principal=1000, annual_rate=10.0, years=5, compounds_per_year=1)
    assert result["growth_factor"] == pytest.approx(1.61051, rel=1e-3)
