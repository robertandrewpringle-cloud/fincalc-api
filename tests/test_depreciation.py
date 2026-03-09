from api.calculators.depreciation import calculate_depreciation
import pytest

def test_straight_line():
    result = calculate_depreciation(
        asset_value=10_000, salvage_value=1_000,
        useful_life_years=5, method="straight_line"
    )
    assert result["annual_depreciation"] == pytest.approx(1800.0, rel=1e-3)
    assert len(result["schedule"]) == 5
    assert result["schedule"][-1]["book_value"] == pytest.approx(1000.0, rel=1e-3)

def test_declining_balance():
    result = calculate_depreciation(
        asset_value=10_000, salvage_value=1_000,
        useful_life_years=5, method="declining_balance"
    )
    assert result["schedule"][0]["depreciation"] > result["schedule"][1]["depreciation"]

def test_invalid_method_raises():
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        calculate_depreciation(asset_value=10_000, salvage_value=1_000,
                               useful_life_years=5, method="magic")
