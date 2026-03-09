from fastapi import APIRouter, Query, HTTPException
from api.calculators.amortization import calculate_amortization
from api.calculators.compound_interest import calculate_compound_interest
from api.calculators.roi import calculate_roi
from api.calculators.npv import calculate_npv
from api.calculators.irr import calculate_irr
from api.calculators.break_even import calculate_break_even
from api.calculators.depreciation import calculate_depreciation
from api.calculators.mortgage import calculate_mortgage

router = APIRouter()

@router.get("/amortize", summary="Loan Amortization Schedule")
def amortize(
    principal: float = Query(..., description="Loan principal amount"),
    annual_rate: float = Query(..., description="Annual interest rate (e.g. 5.0 for 5%)"),
    term_months: int = Query(..., description="Loan term in months"),
):
    return calculate_amortization(principal, annual_rate, term_months)

@router.get("/compound-interest", summary="Compound Interest")
def compound_interest(
    principal: float = Query(..., description="Initial principal"),
    annual_rate: float = Query(..., description="Annual rate (e.g. 5.0 for 5%)"),
    years: int = Query(..., description="Investment duration in years"),
    compounds_per_year: int = Query(12, description="Compounding frequency per year"),
):
    return calculate_compound_interest(principal, annual_rate, years, compounds_per_year)

@router.get("/roi", summary="Return on Investment")
def roi(
    initial_investment: float = Query(...),
    final_value: float = Query(...),
    years: float = Query(1.0, description="Investment duration in years"),
):
    return calculate_roi(initial_investment, final_value, years)

@router.get("/npv", summary="Net Present Value")
def npv(
    rate: float = Query(..., description="Discount rate (e.g. 10.0 for 10%)"),
    cash_flows: str = Query(..., description="Comma-separated cash flows, first is initial investment (negative)"),
):
    try:
        flows = [float(x) for x in cash_flows.split(",")]
    except ValueError:
        raise HTTPException(status_code=422, detail="cash_flows must be comma-separated numbers, e.g. -1000,400,400")
    return calculate_npv(rate, flows)

@router.get("/irr", summary="Internal Rate of Return")
def irr(
    cash_flows: str = Query(..., description="Comma-separated cash flows, first must be negative"),
):
    try:
        flows = [float(x) for x in cash_flows.split(",")]
    except ValueError:
        raise HTTPException(status_code=422, detail="cash_flows must be comma-separated numbers, e.g. -1000,400,400")
    return calculate_irr(flows)

@router.get("/break-even", summary="Break-Even Analysis")
def break_even(
    fixed_costs: float = Query(...),
    variable_cost_per_unit: float = Query(...),
    price_per_unit: float = Query(...),
):
    return calculate_break_even(fixed_costs, variable_cost_per_unit, price_per_unit)

@router.get("/depreciation", summary="Asset Depreciation")
def depreciation(
    asset_value: float = Query(...),
    salvage_value: float = Query(...),
    useful_life_years: int = Query(...),
    method: str = Query("straight_line", description="'straight_line' or 'declining_balance'"),
):
    return calculate_depreciation(asset_value, salvage_value, useful_life_years, method)

@router.get("/mortgage", summary="Mortgage Payment Calculator")
def mortgage(
    home_price: float = Query(...),
    down_payment: float = Query(...),
    annual_rate: float = Query(...),
    term_years: int = Query(...),
):
    return calculate_mortgage(home_price, down_payment, annual_rate, term_years)
