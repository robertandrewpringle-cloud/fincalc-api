# FinCalc API Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build and deploy a financial calculator REST API on RapidAPI marketplace earning passive income.

**Architecture:** Pure-computation FastAPI app with 8 endpoints (no database, no external APIs). Nginx reverse proxy handles SSL. Docker Compose manages the stack. RapidAPI marketplace handles billing, auth, and discovery.

**Tech Stack:** Python 3.12, FastAPI, Uvicorn, Nginx, Docker Compose, Hetzner CX11, RapidAPI

---

## Project Structure

```
api/
├── __init__.py
├── main.py
├── calculators/
│   ├── __init__.py
│   ├── amortization.py
│   ├── compound_interest.py
│   ├── roi.py
│   ├── npv.py
│   ├── irr.py
│   ├── break_even.py
│   ├── depreciation.py
│   └── mortgage.py
tests/
├── __init__.py
├── test_amortization.py
├── test_compound_interest.py
├── test_roi.py
├── test_npv.py
├── test_irr.py
├── test_break_even.py
├── test_depreciation.py
└── test_mortgage.py
docker/
├── Dockerfile
└── nginx.conf
docker-compose.yml
requirements.txt
README.md
```

---

## Task 1: Project Bootstrap

**Files:**
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `api/__init__.py`
- Create: `tests/__init__.py`

**Step 1: Create requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.0
```

**Step 2: Create requirements-dev.txt**

```
pytest==8.3.0
pytest-asyncio==0.24.0
httpx==0.27.0
```

**Step 3: Create empty init files**

```python
# api/__init__.py  — empty
# tests/__init__.py — empty
```

**Step 4: Install dependencies**

Run: `pip install -r requirements.txt -r requirements-dev.txt`
Expected: All packages installed with no errors.

**Step 5: Commit**

```bash
git add requirements.txt requirements-dev.txt api/__init__.py tests/__init__.py
git commit -m "chore: bootstrap project dependencies"
```

---

## Task 2: FastAPI App Skeleton

**Files:**
- Create: `api/main.py`
- Create: `tests/test_health.py`

**Step 1: Write the failing test**

```python
# tests/test_health.py
from httpx import AsyncClient, ASGITransport
import pytest

@pytest.mark.asyncio
async def test_health_check():
    from api.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_health.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'api.main'`

**Step 3: Write minimal implementation**

```python
# api/main.py
from fastapi import FastAPI

app = FastAPI(
    title="FinCalc API",
    description="Financial calculation endpoints for developers. Skip the math.",
    version="1.0.0",
)

@app.get("/health")
def health():
    return {"status": "ok"}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_health.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add api/main.py tests/test_health.py
git commit -m "feat: add FastAPI skeleton with health endpoint"
```

---

## Task 3: Amortization Calculator

**Files:**
- Create: `api/calculators/amortization.py`
- Create: `tests/test_amortization.py`

**Step 1: Write the failing test**

```python
# tests/test_amortization.py
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_amortization.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# api/calculators/__init__.py  — empty

# api/calculators/amortization.py
def calculate_amortization(principal: float, annual_rate: float, term_months: int) -> dict:
    """
    Calculate full amortization schedule.
    annual_rate: percentage, e.g. 5.0 for 5%
    """
    monthly_rate = annual_rate / 100 / 12

    if monthly_rate == 0:
        monthly_payment = principal / term_months
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** term_months) / \
                          ((1 + monthly_rate) ** term_months - 1)

    schedule = []
    balance = principal

    for month in range(1, term_months + 1):
        interest = round(balance * monthly_rate, 2)
        principal_payment = round(monthly_payment - interest, 2)
        balance = round(balance - principal_payment, 2)
        if month == term_months:
            balance = 0.0
        schedule.append({
            "month": month,
            "payment": round(monthly_payment, 2),
            "principal": principal_payment,
            "interest": interest,
            "balance": balance,
        })

    total_payment = round(monthly_payment * term_months, 2)
    total_interest = round(total_payment - principal, 2)

    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_payment": total_payment,
        "total_interest": total_interest,
        "schedule": schedule,
    }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_amortization.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add api/calculators/__init__.py api/calculators/amortization.py tests/test_amortization.py
git commit -m "feat: add amortization calculator"
```

---

## Task 4: Compound Interest Calculator

**Files:**
- Create: `api/calculators/compound_interest.py`
- Create: `tests/test_compound_interest.py`

**Step 1: Write the failing test**

```python
# tests/test_compound_interest.py
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_compound_interest.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# api/calculators/compound_interest.py
def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 12,
) -> dict:
    """A = P(1 + r/n)^(nt)"""
    r = annual_rate / 100
    n = compounds_per_year
    t = years

    final_amount = principal * (1 + r / n) ** (n * t)
    total_interest = final_amount - principal
    growth_factor = final_amount / principal

    return {
        "final_amount": round(final_amount, 2),
        "total_interest": round(total_interest, 2),
        "growth_factor": round(growth_factor, 5),
        "principal": principal,
        "annual_rate": annual_rate,
        "years": years,
        "compounds_per_year": compounds_per_year,
    }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_compound_interest.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add api/calculators/compound_interest.py tests/test_compound_interest.py
git commit -m "feat: add compound interest calculator"
```

---

## Task 5: ROI Calculator

**Files:**
- Create: `api/calculators/roi.py`
- Create: `tests/test_roi.py`

**Step 1: Write the failing test**

```python
# tests/test_roi.py
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_roi.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# api/calculators/roi.py
def calculate_roi(initial_investment: float, final_value: float, years: float = 1.0) -> dict:
    profit_loss = final_value - initial_investment
    roi_percent = (profit_loss / initial_investment) * 100
    annualized_roi_percent = ((final_value / initial_investment) ** (1 / years) - 1) * 100

    return {
        "roi_percent": round(roi_percent, 4),
        "annualized_roi_percent": round(annualized_roi_percent, 4),
        "profit_loss": round(profit_loss, 2),
        "initial_investment": initial_investment,
        "final_value": final_value,
        "years": years,
    }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_roi.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add api/calculators/roi.py tests/test_roi.py
git commit -m "feat: add ROI calculator"
```

---

## Task 6: NPV Calculator

**Files:**
- Create: `api/calculators/npv.py`
- Create: `tests/test_npv.py`

**Step 1: Write the failing test**

```python
# tests/test_npv.py
from api.calculators.npv import calculate_npv
import pytest

def test_profitable_project():
    # Initial investment -1000, cash flows 400/year for 3 years at 10%
    cash_flows = [-1000, 400, 400, 400]
    result = calculate_npv(rate=10.0, cash_flows=cash_flows)
    assert result["npv"] == pytest.approx(-0.53, abs=0.1)
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_npv.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# api/calculators/npv.py
def calculate_npv(rate: float, cash_flows: list[float]) -> dict:
    """NPV = sum(CF_t / (1+r)^t) for t=0..n"""
    r = rate / 100
    npv = sum(cf / (1 + r) ** t for t, cf in enumerate(cash_flows))

    return {
        "npv": round(npv, 2),
        "is_profitable": npv > 0,
        "rate": rate,
        "cash_flows": cash_flows,
        "num_periods": len(cash_flows) - 1,
    }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_npv.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add api/calculators/npv.py tests/test_npv.py
git commit -m "feat: add NPV calculator"
```

---

## Task 7: IRR Calculator

**Files:**
- Create: `api/calculators/irr.py`
- Create: `tests/test_irr.py`

**Step 1: Write the failing test**

```python
# tests/test_irr.py
from api.calculators.irr import calculate_irr
import pytest

def test_basic_irr():
    # -1000 now, +1100 in year 1 → 10% IRR
    cash_flows = [-1000, 1100]
    result = calculate_irr(cash_flows=cash_flows)
    assert result["irr_percent"] == pytest.approx(10.0, rel=1e-3)

def test_multi_period_irr():
    cash_flows = [-1000, 300, 400, 500]
    result = calculate_irr(cash_flows=cash_flows)
    assert result["irr_percent"] == pytest.approx(17.27, rel=1e-2)

def test_irr_no_solution_raises():
    # All positive cash flows → no IRR
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        calculate_irr(cash_flows=[100, 200, 300])
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_irr.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# api/calculators/irr.py
from fastapi import HTTPException

def _npv_at_rate(cash_flows: list[float], rate: float) -> float:
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))

def calculate_irr(cash_flows: list[float]) -> dict:
    """Newton-Raphson IRR. Raises 422 if no solution found."""
    if cash_flows[0] >= 0:
        raise HTTPException(status_code=422, detail="First cash flow must be negative (initial investment).")

    rate = 0.1  # initial guess
    for _ in range(1000):
        npv = _npv_at_rate(cash_flows, rate)
        dnpv = sum(-t * cf / (1 + rate) ** (t + 1) for t, cf in enumerate(cash_flows))
        if abs(dnpv) < 1e-12:
            break
        rate_new = rate - npv / dnpv
        if abs(rate_new - rate) < 1e-8:
            rate = rate_new
            break
        rate = rate_new

    if not (-1 < rate < 100):
        raise HTTPException(status_code=422, detail="Could not converge to a valid IRR for these cash flows.")

    return {
        "irr_percent": round(rate * 100, 4),
        "cash_flows": cash_flows,
        "num_periods": len(cash_flows) - 1,
    }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_irr.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add api/calculators/irr.py tests/test_irr.py
git commit -m "feat: add IRR calculator with Newton-Raphson"
```

---

## Task 8: Break-Even Calculator

**Files:**
- Create: `api/calculators/break_even.py`
- Create: `tests/test_break_even.py`

**Step 1: Write the failing test**

```python
# tests/test_break_even.py
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_break_even.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# api/calculators/break_even.py
from fastapi import HTTPException

def calculate_break_even(fixed_costs: float, variable_cost_per_unit: float, price_per_unit: float) -> dict:
    contribution_margin = price_per_unit - variable_cost_per_unit
    if contribution_margin <= 0:
        raise HTTPException(status_code=422, detail="Price per unit must exceed variable cost per unit.")

    break_even_units = fixed_costs / contribution_margin
    break_even_revenue = break_even_units * price_per_unit
    contribution_margin_ratio = contribution_margin / price_per_unit

    return {
        "break_even_units": round(break_even_units, 2),
        "break_even_revenue": round(break_even_revenue, 2),
        "contribution_margin": round(contribution_margin, 2),
        "contribution_margin_ratio": round(contribution_margin_ratio, 4),
        "fixed_costs": fixed_costs,
        "variable_cost_per_unit": variable_cost_per_unit,
        "price_per_unit": price_per_unit,
    }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_break_even.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add api/calculators/break_even.py tests/test_break_even.py
git commit -m "feat: add break-even calculator"
```

---

## Task 9: Depreciation Calculator

**Files:**
- Create: `api/calculators/depreciation.py`
- Create: `tests/test_depreciation.py`

**Step 1: Write the failing test**

```python
# tests/test_depreciation.py
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_depreciation.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# api/calculators/depreciation.py
from fastapi import HTTPException

def calculate_depreciation(
    asset_value: float,
    salvage_value: float,
    useful_life_years: int,
    method: str = "straight_line",
) -> dict:
    if method not in ("straight_line", "declining_balance"):
        raise HTTPException(status_code=422, detail="method must be 'straight_line' or 'declining_balance'.")

    depreciable_value = asset_value - salvage_value
    schedule = []

    if method == "straight_line":
        annual_depreciation = depreciable_value / useful_life_years
        book_value = asset_value
        for year in range(1, useful_life_years + 1):
            book_value = round(book_value - annual_depreciation, 2)
            if year == useful_life_years:
                book_value = salvage_value
            schedule.append({"year": year, "depreciation": round(annual_depreciation, 2), "book_value": book_value})
        return {"method": method, "annual_depreciation": round(annual_depreciation, 2), "schedule": schedule}

    else:  # declining_balance
        rate = 2 / useful_life_years  # double-declining
        book_value = asset_value
        for year in range(1, useful_life_years + 1):
            depreciation = round(book_value * rate, 2)
            if book_value - depreciation < salvage_value:
                depreciation = round(book_value - salvage_value, 2)
            book_value = round(book_value - depreciation, 2)
            schedule.append({"year": year, "depreciation": depreciation, "book_value": book_value})
        return {"method": method, "annual_depreciation": schedule[0]["depreciation"], "schedule": schedule}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_depreciation.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add api/calculators/depreciation.py tests/test_depreciation.py
git commit -m "feat: add depreciation calculator (straight-line + declining balance)"
```

---

## Task 10: Mortgage Calculator

**Files:**
- Create: `api/calculators/mortgage.py`
- Create: `tests/test_mortgage.py`

**Step 1: Write the failing test**

```python
# tests/test_mortgage.py
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_mortgage.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# api/calculators/mortgage.py
def calculate_mortgage(home_price: float, down_payment: float, annual_rate: float, term_years: int) -> dict:
    loan_amount = home_price - down_payment
    monthly_rate = annual_rate / 100 / 12
    n = term_years * 12

    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
    total_payment = monthly_payment * n
    total_interest = total_payment - loan_amount

    return {
        "loan_amount": round(loan_amount, 2),
        "monthly_payment": round(monthly_payment, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "down_payment_percent": round(down_payment / home_price * 100, 2),
        "home_price": home_price,
        "down_payment": down_payment,
        "annual_rate": annual_rate,
        "term_years": term_years,
    }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_mortgage.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add api/calculators/mortgage.py tests/test_mortgage.py
git commit -m "feat: add mortgage calculator"
```

---

## Task 11: Wire All Endpoints Into FastAPI Routes

**Files:**
- Create: `api/routes/__init__.py`
- Create: `api/routes/calculators.py`
- Modify: `api/main.py`
- Create: `tests/test_routes.py`

**Step 1: Write the failing test**

```python
# tests/test_routes.py
from httpx import AsyncClient, ASGITransport
import pytest

@pytest.fixture
def app():
    from api.main import app
    return app

@pytest.mark.asyncio
async def test_amortize_endpoint(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/amortize?principal=100000&annual_rate=5.0&term_months=12")
    assert response.status_code == 200
    data = response.json()
    assert "monthly_payment" in data
    assert "schedule" in data

@pytest.mark.asyncio
async def test_mortgage_endpoint(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/mortgage?home_price=300000&down_payment=60000&annual_rate=6.5&term_years=30")
    assert response.status_code == 200
    assert response.json()["monthly_payment"] > 0

@pytest.mark.asyncio
async def test_missing_param_returns_422(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/amortize?principal=100000")  # missing params
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_npv_endpoint(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/npv?rate=10.0&cash_flows=-1000,400,400,400")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_irr_endpoint(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/irr?cash_flows=-1000,1100")
    assert response.status_code == 200
    assert response.json()["irr_percent"] == pytest.approx(10.0, rel=1e-3)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_routes.py -v`
Expected: FAIL — routes not wired

**Step 3: Create routes module**

```python
# api/routes/__init__.py  — empty

# api/routes/calculators.py
from fastapi import APIRouter, Query
from typing import Annotated
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
    flows = [float(x) for x in cash_flows.split(",")]
    return calculate_npv(rate, flows)

@router.get("/irr", summary="Internal Rate of Return")
def irr(
    cash_flows: str = Query(..., description="Comma-separated cash flows, first must be negative"),
):
    flows = [float(x) for x in cash_flows.split(",")]
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
```

**Step 4: Update main.py to include router**

```python
# api/main.py
from fastapi import FastAPI
from api.routes.calculators import router

app = FastAPI(
    title="FinCalc API",
    description="Financial calculation endpoints for developers. Skip the math. 8 endpoints covering amortization, compound interest, ROI, NPV, IRR, break-even, depreciation, and mortgage.",
    version="1.0.0",
    contact={"name": "FinCalc API", "url": "https://rapidapi.com"},
)

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}
```

**Step 5: Run all tests**

Run: `pytest -v`
Expected: All tests PASS (20+ tests)

**Step 6: Commit**

```bash
git add api/routes/ api/main.py tests/test_routes.py
git commit -m "feat: wire all 8 calculator endpoints into FastAPI routes"
```

---

## Task 12: Docker + Nginx Production Config

**Files:**
- Create: `docker/Dockerfile`
- Create: `docker/nginx.conf`
- Create: `docker-compose.yml`
- Create: `.env.example`

**Step 1: Create Dockerfile**

```dockerfile
# docker/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ api/

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

**Step 2: Create nginx.conf**

```nginx
# docker/nginx.conf
events { worker_connections 1024; }

http {
    upstream api {
        server api:8000;
    }

    server {
        listen 80;
        server_name _;

        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

**Step 3: Create docker-compose.yml**

```yaml
# docker-compose.yml
version: "3.9"

services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - api
    restart: unless-stopped
```

**Step 4: Create .env.example**

```
ENVIRONMENT=production
```

**Step 5: Build and smoke test locally**

Run: `docker compose build`
Expected: Build completes without errors.

Run: `docker compose up -d`
Expected: Containers start.

Run: `curl http://localhost/health`
Expected: `{"status":"ok"}`

Run: `docker compose down`

**Step 6: Commit**

```bash
git add docker/ docker-compose.yml .env.example
git commit -m "chore: add Docker + Nginx production config"
```

---

## Task 13: Deployment Script

**Files:**
- Create: `deploy.sh`

**Step 1: Create deploy.sh**

```bash
#!/bin/bash
# deploy.sh — Run on Hetzner VPS to deploy/update FinCalc API
# Usage: ./deploy.sh
set -e

DOMAIN="${DOMAIN:-fincalcapi.com}"
EMAIL="${EMAIL:-admin@fincalcapi.com}"

echo "==> Installing dependencies..."
apt-get update -qq
apt-get install -y -qq docker.io docker-compose-plugin certbot python3-certbot-nginx git

echo "==> Pulling latest code..."
if [ -d "/opt/fincalcapi" ]; then
    cd /opt/fincalcapi && git pull
else
    git clone https://github.com/YOUR_GITHUB_USERNAME/fincalc-api /opt/fincalcapi
    cd /opt/fincalcapi
fi

echo "==> Obtaining SSL certificate..."
certbot certonly --standalone --non-interactive --agree-tos \
    -m "$EMAIL" -d "$DOMAIN" --pre-hook "docker compose down" \
    --post-hook "docker compose up -d" 2>/dev/null || echo "Cert already exists, skipping."

echo "==> Building and starting containers..."
docker compose build --no-cache
docker compose up -d

echo "==> Verifying deployment..."
sleep 3
curl -sf http://localhost/health && echo "Deployment successful!" || echo "WARNING: health check failed"
```

**Step 2: Make executable and commit**

```bash
chmod +x deploy.sh
git add deploy.sh
git commit -m "chore: add one-command deployment script"
```

---

## Task 14: README and GitHub Repository Content

**Files:**
- Create: `README.md`

**Step 1: Create README.md**

````markdown
# FinCalc API

> Financial calculation endpoints for developers. Skip the math.

Available on [RapidAPI](https://rapidapi.com) — billing, authentication, and rate limiting handled by the marketplace.

## Endpoints

| Endpoint | Description |
|---|---|
| `GET /amortize` | Full loan amortization schedule |
| `GET /compound-interest` | Savings and investment projections |
| `GET /roi` | Return on investment |
| `GET /npv` | Net present value |
| `GET /irr` | Internal rate of return |
| `GET /break-even` | Break-even analysis |
| `GET /depreciation` | Straight-line & declining balance |
| `GET /mortgage` | Monthly payment + total cost |

## Quick Examples

**Amortization (Python):**
```python
import requests

url = "https://fincalcapi.p.rapidapi.com/amortize"
params = {"principal": 100000, "annual_rate": 5.0, "term_months": 360}
headers = {
    "X-RapidAPI-Key": "YOUR_API_KEY",
    "X-RapidAPI-Host": "fincalcapi.p.rapidapi.com"
}
response = requests.get(url, headers=headers, params=params)
print(response.json()["monthly_payment"])  # 536.82
```

**Mortgage (JavaScript):**
```javascript
const response = await fetch(
  'https://fincalcapi.p.rapidapi.com/mortgage?home_price=300000&down_payment=60000&annual_rate=6.5&term_years=30',
  { headers: { 'X-RapidAPI-Key': 'YOUR_API_KEY', 'X-RapidAPI-Host': 'fincalcapi.p.rapidapi.com' } }
);
const data = await response.json();
console.log(data.monthly_payment); // 1517.47
```

## Self-Hosting

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/fincalc-api
cd fincalc-api
docker compose up -d
curl http://localhost/health
```

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```
````

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with endpoint reference and code examples"
```

---

## Task 15: RapidAPI Listing Content

**Files:**
- Create: `docs/rapidapi-listing.md`

**Step 1: Create the listing copy**

```markdown
# docs/rapidapi-listing.md — RapidAPI Listing Copy

## Short Description (160 chars)
Financial calculation APIs for developers. Amortization, mortgage, ROI, NPV, IRR, compound interest, break-even, depreciation.

## Long Description

**Stop reimplementing financial math.** FinCalc API gives you 8 production-ready financial calculation endpoints so you can ship features faster.

### What's included

- **Amortization** — Full payment schedule with principal, interest, and balance per period
- **Compound Interest** — Final value, total interest, and growth factor for any compounding frequency
- **ROI** — Simple and annualized return on investment
- **NPV** — Net present value at any discount rate
- **IRR** — Internal rate of return via Newton-Raphson convergence
- **Break-Even** — Units and revenue needed to cover fixed costs, with contribution margin
- **Depreciation** — Straight-line and double-declining balance schedules
- **Mortgage** — Monthly payment, total cost, and interest for any loan

### Use cases

- Fintech apps and dashboards
- Accounting and bookkeeping tools
- Real estate calculators
- Business plan tools
- Personal finance apps
- SaaS pricing calculators

### Design

- All results in JSON
- All inputs as query parameters
- No API keys stored — stateless computation only
- Sub-50ms response times

## Tags
finance, calculator, mortgage, amortization, ROI, NPV, IRR, fintech, investment, loan

## Website
https://github.com/YOUR_GITHUB_USERNAME/fincalc-api
```

**Step 2: Commit**

```bash
git add docs/rapidapi-listing.md
git commit -m "docs: add RapidAPI listing copy"
```

---

## Task 16: Launch Checklist

After all code tasks complete, execute in order:

1. **Push to GitHub** — `git push origin main`
2. **VPS setup** — Provision Hetzner CX11, purchase domain, point DNS
3. **Deploy** — SSH into VPS, run `./deploy.sh`
4. **Verify live** — `curl https://fincalcapi.com/health`
5. **RapidAPI listing** — Create provider account, add new API, paste listing copy from `docs/rapidapi-listing.md`, import OpenAPI spec from `https://fincalcapi.com/openapi.json`
6. **Set pricing tiers** — Free (50/day), Basic $9.99 (1000/day), Pro $29.99 (10k/day), Ultra $99.99 (unlimited)
7. **GitHub repo public** — Enable public visibility
8. **Post Show HN** — "Show HN: FinCalc API — 8 financial calculation endpoints for developers"
9. **Post ProductHunt** — Schedule for Tuesday 12:01am PST
10. **Post Dev.to articles** — Publish 3 tutorials (drafts in `docs/articles/`)

---

## Running the Full Test Suite

```bash
pytest -v --tb=short
```

Expected: 25+ tests, all PASS.
```
