# BizCal API Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build BizCal API — a business calendar REST API with 22 endpoints covering business day math, working hours, holiday calendars (15 countries + sub-national regions), and calendar intelligence — listed on RapidAPI marketplace as an income-generating product.

**Architecture:** Pure-computation FastAPI service, zero external API calls. Holiday data from the `holidays` Python library (pip install, actively maintained, 200+ region calendars). Timezone math via Python stdlib `zoneinfo`. Mirrors FinCalc's structure: `api/calculators/` for pure logic, `api/routes/` for HTTP layer.

**Tech Stack:** Python 3.12, FastAPI, Uvicorn, `holidays` library, `zoneinfo` (stdlib), Nginx, Docker Compose, Hetzner CX11 VPS, RapidAPI marketplace.

**New project directory:** `E:/CLAUDE/PROJECT - BIZCAL/`

---

## Task 1: Project Scaffold

**Files:**
- Create: `E:/CLAUDE/PROJECT - BIZCAL/` (new directory)
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `api/__init__.py`
- Create: `api/main.py`
- Create: `api/routes/__init__.py`
- Create: `api/calculators/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

**Step 1: Create project directory and git repo**

```bash
mkdir -p "E:/CLAUDE/PROJECT - BIZCAL"
cd "E:/CLAUDE/PROJECT - BIZCAL"
git init
```

**Step 2: Create requirements.txt**

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
holidays==0.65
pydantic==2.10.6
```

**Step 3: Create requirements-dev.txt**

```
pytest==8.3.5
httpx==0.28.1
pytest-cov==6.0.0
```

**Step 4: Create directory structure**

```bash
mkdir -p api/routes api/calculators tests docker docs
touch api/__init__.py api/routes/__init__.py api/calculators/__init__.py tests/__init__.py
```

**Step 5: Create api/main.py**

```python
from fastapi import FastAPI
from api.routes.business_days import router as business_days_router
from api.routes.working_hours import router as working_hours_router
from api.routes.holidays import router as holidays_router
from api.routes.calendar import router as calendar_router
from api.routes.bulk import router as bulk_router

app = FastAPI(
    title="BizCal API",
    description=(
        "Business calendar API for developers. Business days, working hours, "
        "and holiday calendars for 15 countries with sub-national regions. "
        "22 endpoints covering business day math, SLA deadlines, fiscal years, "
        "and calendar intelligence."
    ),
    version="1.0.0",
    contact={"name": "BizCal API", "url": "https://rapidapi.com"},
)

app.include_router(business_days_router, prefix="/business-days", tags=["Business Days"])
app.include_router(working_hours_router, prefix="/working-hours", tags=["Working Hours"])
app.include_router(holidays_router, prefix="/holidays", tags=["Holidays"])
app.include_router(calendar_router, prefix="/calendar", tags=["Calendar"])
app.include_router(bulk_router, tags=["Bulk"])


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
```

**Step 6: Create tests/conftest.py**

```python
from fastapi.testclient import TestClient
from api.main import app
import pytest

@pytest.fixture
def client():
    return TestClient(app)
```

**Step 7: Write a smoke test**

Create `tests/test_health.py`:
```python
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
```

**Step 8: Run smoke test (expect FAIL — routes not yet created)**

```bash
cd "E:/CLAUDE/PROJECT - BIZCAL"
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/test_health.py -v
```
Expected: ImportError because route modules don't exist yet. That's correct — we build routes in subsequent tasks.

**Step 9: Create stub route files so imports resolve**

Create `api/routes/business_days.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

Create `api/routes/working_hours.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

Create `api/routes/holidays.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

Create `api/routes/calendar.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

Create `api/routes/bulk.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

**Step 10: Run smoke test (expect PASS)**

```bash
pytest tests/test_health.py -v
```
Expected: PASS

**Step 11: Commit**

```bash
git add -A
git commit -m "chore: project scaffold, health endpoint, stub routes"
```

---

## Task 2: Holiday Registry (Calculator)

The holiday registry is the foundation all other calculators depend on. Build it first.

**Files:**
- Create: `api/calculators/holidays.py`
- Create: `tests/test_holidays_calc.py`

**Step 1: Write failing tests**

Create `tests/test_holidays_calc.py`:
```python
import pytest
from datetime import date
from api.calculators.holidays import get_holidays, is_holiday, list_holidays, next_holiday, supported_countries

class TestGetHolidays:
    def test_us_federal_christmas(self):
        h = get_holidays(2024, "US")
        assert date(2024, 12, 25) in h

    def test_us_state_texas_independence(self):
        h = get_holidays(2024, "US", "TX")
        assert date(2024, 3, 2) in h

    def test_uk_england_boxing_day(self):
        h = get_holidays(2024, "GB")
        assert date(2024, 12, 26) in h

    def test_germany_land_bavarian_holiday(self):
        # Assumption of Mary is specific to Bavaria (BY)
        h = get_holidays(2024, "DE", "BY")
        assert date(2024, 8, 15) in h

    def test_invalid_country_returns_empty(self):
        h = get_holidays(2024, "XX")
        assert h == {}

    def test_invalid_region_returns_national_only(self):
        # Falls back to national holidays if region is invalid
        h = get_holidays(2024, "US", "INVALID")
        assert date(2024, 7, 4) in h  # Independence Day is national


class TestIsHoliday:
    def test_christmas_is_holiday(self):
        assert is_holiday(date(2024, 12, 25), "US") is True

    def test_regular_day_is_not_holiday(self):
        assert is_holiday(date(2024, 3, 15), "US") is False

    def test_weekend_is_not_holiday(self):
        # Weekends are not public holidays
        assert is_holiday(date(2024, 1, 6), "US") is False  # Saturday

    def test_observed_holiday(self):
        # July 4 2026 falls on Saturday; observed Friday July 3
        assert is_holiday(date(2026, 7, 3), "US") is True


class TestListHolidays:
    def test_returns_list_of_dicts(self):
        result = list_holidays(2024, "US")
        assert isinstance(result, list)
        assert len(result) > 0
        assert "date" in result[0]
        assert "name" in result[0]

    def test_sorted_by_date(self):
        result = list_holidays(2024, "US")
        dates = [r["date"] for r in result]
        assert dates == sorted(dates)

    def test_uk_scotland_has_st_andrews(self):
        result = list_holidays(2024, "GB", "SCT")
        names = [r["name"] for r in result]
        assert any("Andrew" in n for n in names)


class TestNextHoliday:
    def test_next_holiday_after_christmas(self):
        result = next_holiday(date(2024, 12, 26), "US")
        assert result["date"] > date(2024, 12, 26)

    def test_day_before_christmas_returns_christmas(self):
        result = next_holiday(date(2024, 12, 24), "US")
        assert result["date"] == date(2024, 12, 25)

    def test_on_holiday_returns_next_one(self):
        # On Christmas, next holiday is NOT Christmas itself
        result = next_holiday(date(2024, 12, 25), "US")
        assert result["date"] > date(2024, 12, 25)


class TestSupportedCountries:
    def test_returns_dict(self):
        result = supported_countries()
        assert isinstance(result, dict)

    def test_us_has_states(self):
        result = supported_countries()
        assert "US" in result
        assert "TX" in result["US"]["regions"]
        assert "CA" in result["US"]["regions"]

    def test_gb_has_subdivisions(self):
        result = supported_countries()
        assert "GB" in result
        assert "ENG" in result["GB"]["regions"]
        assert "SCT" in result["GB"]["regions"]

    def test_fifteen_countries(self):
        result = supported_countries()
        assert len(result) == 15
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_holidays_calc.py -v
```
Expected: ImportError — `api.calculators.holidays` doesn't exist yet.

**Step 3: Implement api/calculators/holidays.py**

```python
from datetime import date, timedelta
from typing import Optional
import holidays as holidays_lib

# Supported country registry with metadata and sub-national regions
SUPPORTED_COUNTRIES = {
    "US": {
        "name": "United States",
        "code": "US",
        "regions": {
            "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
            "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DC": "District of Columbia",
            "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
            "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
            "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
            "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
            "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
            "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
            "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
            "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
            "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
            "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
            "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
        },
    },
    "GB": {
        "name": "United Kingdom",
        "code": "GB",
        "regions": {
            "ENG": "England", "NIR": "Northern Ireland", "SCT": "Scotland", "WLS": "Wales",
        },
    },
    "CA": {
        "name": "Canada",
        "code": "CA",
        "regions": {
            "AB": "Alberta", "BC": "British Columbia", "MB": "Manitoba",
            "NB": "New Brunswick", "NL": "Newfoundland and Labrador",
            "NS": "Nova Scotia", "NT": "Northwest Territories", "NU": "Nunavut",
            "ON": "Ontario", "PE": "Prince Edward Island", "QC": "Quebec",
            "SK": "Saskatchewan", "YT": "Yukon",
        },
    },
    "AU": {
        "name": "Australia",
        "code": "AU",
        "regions": {
            "ACT": "Australian Capital Territory", "NSW": "New South Wales",
            "NT": "Northern Territory", "QLD": "Queensland",
            "SA": "South Australia", "TAS": "Tasmania",
            "VIC": "Victoria", "WA": "Western Australia",
        },
    },
    "DE": {
        "name": "Germany",
        "code": "DE",
        "regions": {
            "BB": "Brandenburg", "BE": "Berlin", "BW": "Baden-Württemberg",
            "BY": "Bavaria", "HB": "Bremen", "HE": "Hesse", "HH": "Hamburg",
            "MV": "Mecklenburg-Vorpommern", "NI": "Lower Saxony",
            "NW": "North Rhine-Westphalia", "RP": "Rhineland-Palatinate",
            "SH": "Schleswig-Holstein", "SL": "Saarland", "SN": "Saxony",
            "ST": "Saxony-Anhalt", "TH": "Thuringia",
        },
    },
    "FR": {"name": "France", "code": "FR", "regions": {}},
    "ES": {
        "name": "Spain",
        "code": "ES",
        "regions": {
            "AN": "Andalusia", "AR": "Aragon", "AS": "Asturias",
            "CB": "Cantabria", "CE": "Ceuta", "CL": "Castile and León",
            "CM": "Castile-La Mancha", "CN": "Canary Islands",
            "CT": "Catalonia", "EX": "Extremadura", "GA": "Galicia",
            "IB": "Balearic Islands", "LO": "La Rioja", "MA": "Madrid",
            "MC": "Region of Murcia", "ML": "Melilla", "MU": "Murcia",
            "NA": "Navarre", "PV": "Basque Country", "RI": "La Rioja",
            "VC": "Valencian Community",
        },
    },
    "IT": {"name": "Italy", "code": "IT", "regions": {}},
    "NL": {"name": "Netherlands", "code": "NL", "regions": {}},
    "BR": {
        "name": "Brazil",
        "code": "BR",
        "regions": {
            "AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá",
            "BA": "Bahia", "CE": "Ceará", "DF": "Federal District",
            "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
            "MG": "Minas Gerais", "MS": "Mato Grosso do Sul", "MT": "Mato Grosso",
            "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco", "PI": "Piauí",
            "PR": "Paraná", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
            "RO": "Rondônia", "RR": "Roraima", "RS": "Rio Grande do Sul",
            "SC": "Santa Catarina", "SE": "Sergipe", "SP": "São Paulo", "TO": "Tocantins",
        },
    },
    "IN": {
        "name": "India",
        "code": "IN",
        "regions": {
            "AN": "Andaman and Nicobar Islands", "AP": "Andhra Pradesh",
            "AR": "Arunachal Pradesh", "AS": "Assam", "BR": "Bihar",
            "CG": "Chhattisgarh", "CH": "Chandigarh", "DD": "Daman and Diu",
            "DL": "Delhi", "DN": "Dadra and Nagar Haveli", "GA": "Goa",
            "GJ": "Gujarat", "HP": "Himachal Pradesh", "HR": "Haryana",
            "JH": "Jharkhand", "JK": "Jammu and Kashmir", "KA": "Karnataka",
            "KL": "Kerala", "LA": "Ladakh", "LD": "Lakshadweep",
            "MH": "Maharashtra", "ML": "Meghalaya", "MN": "Manipur",
            "MP": "Madhya Pradesh", "MZ": "Mizoram", "NL": "Nagaland",
            "OR": "Odisha", "PB": "Punjab", "PY": "Puducherry",
            "RJ": "Rajasthan", "SK": "Sikkim", "TN": "Tamil Nadu",
            "TR": "Tripura", "TS": "Telangana", "UK": "Uttarakhand",
            "UP": "Uttar Pradesh", "WB": "West Bengal",
        },
    },
    "JP": {"name": "Japan", "code": "JP", "regions": {}},
    "SG": {"name": "Singapore", "code": "SG", "regions": {}},
    "ZA": {"name": "South Africa", "code": "ZA", "regions": {}},
    "NZ": {
        "name": "New Zealand",
        "code": "NZ",
        "regions": {
            "AUK": "Auckland", "BOP": "Bay of Plenty", "CAN": "Canterbury",
            "CIT": "Chatham Islands Territory", "GIS": "Gisborne",
            "HKB": "Hawke's Bay", "MBH": "Marlborough", "MWT": "Manawatu-Whanganui",
            "NSN": "Nelson", "NTL": "Northland", "OTA": "Otago",
            "STL": "Southland", "TAS": "Tasman", "TKI": "Taranaki",
            "WGN": "Wellington", "WKO": "Waikato", "WTC": "West Coast",
        },
    },
}


def get_holidays(year: int, country: str, region: Optional[str] = None) -> dict:
    """Return a dict of {date: holiday_name} for the given country/region/year."""
    if country not in SUPPORTED_COUNTRIES:
        return {}
    try:
        if region and region in SUPPORTED_COUNTRIES[country]["regions"]:
            return holidays_lib.country_holidays(country, subdiv=region, years=year)
        return holidays_lib.country_holidays(country, years=year)
    except (KeyError, NotImplementedError):
        return {}


def is_holiday(d: date, country: str, region: Optional[str] = None) -> bool:
    """Return True if the date is a public holiday (not counting weekends)."""
    h = get_holidays(d.year, country, region)
    return d in h


def list_holidays(year: int, country: str, region: Optional[str] = None) -> list[dict]:
    """Return sorted list of {date, name} dicts for all holidays in a year."""
    h = get_holidays(year, country, region)
    result = [{"date": d, "name": name} for d, name in h.items()]
    return sorted(result, key=lambda x: x["date"])


def next_holiday(from_date: date, country: str, region: Optional[str] = None) -> Optional[dict]:
    """Return the next holiday after from_date (exclusive)."""
    # Search up to 2 years ahead
    for year_offset in range(3):
        year = from_date.year + year_offset
        h = get_holidays(year, country, region)
        for d in sorted(h.keys()):
            if d > from_date:
                return {"date": d, "name": h[d]}
    return None


def supported_countries() -> dict:
    """Return the full registry of supported countries and their regions."""
    return SUPPORTED_COUNTRIES
```

**Step 4: Run tests**

```bash
pytest tests/test_holidays_calc.py -v
```
Expected: All tests PASS. Fix any failures before continuing.

**Step 5: Commit**

```bash
git add api/calculators/holidays.py tests/test_holidays_calc.py
git commit -m "feat: holiday registry and calculator with 15 countries"
```

---

## Task 3: Business Days Calculator

**Files:**
- Create: `api/calculators/business_days.py`
- Create: `tests/test_business_days_calc.py`

**Step 1: Write failing tests**

Create `tests/test_business_days_calc.py`:
```python
import pytest
from datetime import date
from api.calculators.business_days import (
    is_business_day, business_days_between,
    add_business_days, subtract_business_days,
    next_business_day, previous_business_day,
)


class TestIsBusinessDay:
    def test_weekday_is_business_day(self):
        assert is_business_day(date(2024, 3, 11)) is True  # Monday

    def test_saturday_is_not_business_day(self):
        assert is_business_day(date(2024, 3, 9)) is False

    def test_sunday_is_not_business_day(self):
        assert is_business_day(date(2024, 3, 10)) is False

    def test_holiday_is_not_business_day(self):
        assert is_business_day(date(2024, 12, 25), "US") is False

    def test_holiday_on_weekend_not_double_counted(self):
        # Christmas 2022 was on Sunday — Monday Dec 26 is observed
        assert is_business_day(date(2022, 12, 26), "US") is False  # observed holiday
        assert is_business_day(date(2022, 12, 27), "US") is True   # Tuesday is fine

    def test_weekday_with_no_country_ignores_holidays(self):
        assert is_business_day(date(2024, 12, 25)) is True  # Christmas but no country


class TestBusinessDaysBetween:
    def test_same_day_is_zero(self):
        d = date(2024, 3, 11)
        assert business_days_between(d, d) == 0

    def test_one_week_is_five(self):
        assert business_days_between(date(2024, 3, 11), date(2024, 3, 18)) == 5

    def test_excludes_weekend(self):
        # Mon to Mon = 5 business days (Mon-Fri)
        assert business_days_between(date(2024, 3, 4), date(2024, 3, 11)) == 5

    def test_excludes_holiday(self):
        # July 4 2024 is Thursday
        result = business_days_between(date(2024, 7, 1), date(2024, 7, 8), "US")
        # Mon=1, Tue=2, Wed=3, Thu=holiday, Fri=4 → 4 business days
        assert result == 4

    def test_reversed_dates_same_result(self):
        a = date(2024, 3, 11)
        b = date(2024, 3, 18)
        assert business_days_between(a, b) == business_days_between(b, a)

    def test_cross_year_boundary(self):
        # Dec 30 (Mon) to Jan 6 (Mon) = 5 business days (skipping New Year's)
        result = business_days_between(date(2024, 12, 30), date(2025, 1, 6), "US")
        assert result == 4  # Dec 30, 31, Jan 2, 3 (Jan 1 is New Year's)


class TestAddBusinessDays:
    def test_add_five_from_monday(self):
        assert add_business_days(date(2024, 3, 11), 5) == date(2024, 3, 18)

    def test_add_zero_returns_same(self):
        assert add_business_days(date(2024, 3, 11), 0) == date(2024, 3, 11)

    def test_add_crosses_weekend(self):
        assert add_business_days(date(2024, 3, 14), 1) == date(2024, 3, 18)  # Fri+1=Mon

    def test_add_skips_holiday(self):
        # July 3 2024 (Wed) + 1 = July 5 (Fri), skipping July 4 holiday
        assert add_business_days(date(2024, 7, 3), 1, "US") == date(2024, 7, 5)

    def test_add_crosses_year_boundary(self):
        assert add_business_days(date(2024, 12, 31), 1, "US") == date(2025, 1, 2)  # Skip NY


class TestSubtractBusinessDays:
    def test_subtract_five_from_monday(self):
        assert subtract_business_days(date(2024, 3, 18), 5) == date(2024, 3, 11)

    def test_subtract_crosses_weekend(self):
        assert subtract_business_days(date(2024, 3, 18), 1) == date(2024, 3, 15)  # Mon-1=Fri

    def test_subtract_skips_holiday(self):
        assert subtract_business_days(date(2024, 7, 5), 1, "US") == date(2024, 7, 3)  # skip Jul 4


class TestNextPreviousBusinessDay:
    def test_next_from_friday_is_monday(self):
        assert next_business_day(date(2024, 3, 15)) == date(2024, 3, 18)

    def test_next_skips_holiday(self):
        # Dec 24 (Tue) next = Dec 26 (Thu), skipping Christmas
        assert next_business_day(date(2024, 12, 24), "US") == date(2024, 12, 26)

    def test_previous_from_monday_is_friday(self):
        assert previous_business_day(date(2024, 3, 18)) == date(2024, 3, 15)

    def test_previous_skips_holiday(self):
        assert previous_business_day(date(2024, 12, 26), "US") == date(2024, 12, 24)
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_business_days_calc.py -v
```
Expected: ImportError.

**Step 3: Implement api/calculators/business_days.py**

```python
from datetime import date, timedelta
from typing import Optional
from api.calculators.holidays import get_holidays


def is_business_day(d: date, country: Optional[str] = None, region: Optional[str] = None) -> bool:
    if d.weekday() >= 5:
        return False
    if country:
        h = get_holidays(d.year, country, region)
        return d not in h
    return True


def business_days_between(
    start: date, end: date,
    country: Optional[str] = None, region: Optional[str] = None
) -> int:
    if start == end:
        return 0
    if start > end:
        start, end = end, start
    count = 0
    current = start
    # Cache holidays for each year in range
    holiday_cache: dict[int, set] = {}
    while current < end:
        year = current.year
        if year not in holiday_cache:
            holiday_cache[year] = set(get_holidays(year, country, region).keys()) if country else set()
        if current.weekday() < 5 and current not in holiday_cache[year]:
            count += 1
        current += timedelta(days=1)
    return count


def add_business_days(
    start: date, n: int,
    country: Optional[str] = None, region: Optional[str] = None
) -> date:
    if n == 0:
        return start
    if n < 0:
        return subtract_business_days(start, -n, country, region)
    current = start
    remaining = n
    holiday_cache: dict[int, set] = {}
    while remaining > 0:
        current += timedelta(days=1)
        year = current.year
        if year not in holiday_cache:
            holiday_cache[year] = set(get_holidays(year, country, region).keys()) if country else set()
        if current.weekday() < 5 and current not in holiday_cache[year]:
            remaining -= 1
    return current


def subtract_business_days(
    start: date, n: int,
    country: Optional[str] = None, region: Optional[str] = None
) -> date:
    if n == 0:
        return start
    if n < 0:
        return add_business_days(start, -n, country, region)
    current = start
    remaining = n
    holiday_cache: dict[int, set] = {}
    while remaining > 0:
        current -= timedelta(days=1)
        year = current.year
        if year not in holiday_cache:
            holiday_cache[year] = set(get_holidays(year, country, region).keys()) if country else set()
        if current.weekday() < 5 and current not in holiday_cache[year]:
            remaining -= 1
    return current


def next_business_day(
    d: date,
    country: Optional[str] = None, region: Optional[str] = None
) -> date:
    current = d + timedelta(days=1)
    holiday_cache: dict[int, set] = {}
    while True:
        year = current.year
        if year not in holiday_cache:
            holiday_cache[year] = set(get_holidays(year, country, region).keys()) if country else set()
        if current.weekday() < 5 and current not in holiday_cache[year]:
            return current
        current += timedelta(days=1)


def previous_business_day(
    d: date,
    country: Optional[str] = None, region: Optional[str] = None
) -> date:
    current = d - timedelta(days=1)
    holiday_cache: dict[int, set] = {}
    while True:
        year = current.year
        if year not in holiday_cache:
            holiday_cache[year] = set(get_holidays(year, country, region).keys()) if country else set()
        if current.weekday() < 5 and current not in holiday_cache[year]:
            return current
        current -= timedelta(days=1)
```

**Step 4: Run tests**

```bash
pytest tests/test_business_days_calc.py -v
```
Expected: All PASS. Fix any failures.

**Step 5: Commit**

```bash
git add api/calculators/business_days.py tests/test_business_days_calc.py
git commit -m "feat: business days calculator with holiday awareness"
```

---

## Task 4: Working Hours Calculator

**Files:**
- Create: `api/calculators/working_hours.py`
- Create: `tests/test_working_hours_calc.py`

**Step 1: Write failing tests**

Create `tests/test_working_hours_calc.py`:
```python
import pytest
from datetime import datetime, timezone
import zoneinfo
from api.calculators.working_hours import working_hours_between, add_working_hours, calculate_deadline

EST = zoneinfo.ZoneInfo("America/New_York")
UTC = timezone.utc


class TestWorkingHoursBetween:
    def test_same_datetime_is_zero(self):
        dt = datetime(2024, 3, 11, 10, 0, tzinfo=EST)
        assert working_hours_between(dt, dt) == 0.0

    def test_full_day_is_eight_hours(self):
        start = datetime(2024, 3, 11, 9, 0, tzinfo=EST)
        end = datetime(2024, 3, 11, 17, 0, tzinfo=EST)
        assert working_hours_between(start, end) == 8.0

    def test_half_day_is_four_hours(self):
        start = datetime(2024, 3, 11, 9, 0, tzinfo=EST)
        end = datetime(2024, 3, 11, 13, 0, tzinfo=EST)
        assert working_hours_between(start, end) == 4.0

    def test_weekend_hours_excluded(self):
        # Friday 9am to Monday 9am = 8 working hours (Friday only)
        start = datetime(2024, 3, 15, 9, 0, tzinfo=EST)  # Friday
        end = datetime(2024, 3, 18, 9, 0, tzinfo=EST)    # Monday
        assert working_hours_between(start, end) == 8.0

    def test_holiday_hours_excluded(self):
        # Christmas day 2024 (Wed) — 0 working hours
        start = datetime(2024, 12, 25, 9, 0, tzinfo=EST)
        end = datetime(2024, 12, 25, 17, 0, tzinfo=EST)
        assert working_hours_between(start, end, "America/New_York", "US") == 0.0

    def test_before_work_hours_ignored(self):
        start = datetime(2024, 3, 11, 7, 0, tzinfo=EST)  # 7am
        end = datetime(2024, 3, 11, 10, 0, tzinfo=EST)   # 10am
        assert working_hours_between(start, end) == 1.0  # Only 9-10am counts

    def test_after_work_hours_ignored(self):
        start = datetime(2024, 3, 11, 16, 0, tzinfo=EST)
        end = datetime(2024, 3, 11, 19, 0, tzinfo=EST)
        assert working_hours_between(start, end) == 1.0  # Only 16-17 counts

    def test_two_full_days(self):
        start = datetime(2024, 3, 11, 9, 0, tzinfo=EST)  # Monday
        end = datetime(2024, 3, 12, 17, 0, tzinfo=EST)   # Tuesday
        assert working_hours_between(start, end) == 16.0

    def test_naive_datetime_treated_as_utc(self):
        start = datetime(2024, 3, 11, 9, 0)
        end = datetime(2024, 3, 11, 17, 0)
        result = working_hours_between(start, end, "UTC")
        assert result == 8.0


class TestAddWorkingHours:
    def test_add_eight_hours_same_day(self):
        start = datetime(2024, 3, 11, 9, 0, tzinfo=EST)
        result = add_working_hours(start, 8)
        assert result.hour == 17
        assert result.date() == start.date()

    def test_add_crosses_end_of_day(self):
        start = datetime(2024, 3, 11, 15, 0, tzinfo=EST)  # 3pm
        result = add_working_hours(start, 4)  # 4 hours: 3-5pm + 2hrs next day
        assert result == datetime(2024, 3, 12, 11, 0, tzinfo=EST)

    def test_add_crosses_weekend(self):
        start = datetime(2024, 3, 15, 16, 0, tzinfo=EST)  # Friday 4pm
        result = add_working_hours(start, 2)  # 1hr Friday + 1hr Monday
        assert result == datetime(2024, 3, 18, 10, 0, tzinfo=EST)

    def test_add_skips_holiday(self):
        # Jul 3 2024 5pm + 1 working hour = Jul 5 10am (skip Jul 4)
        start = datetime(2024, 7, 3, 16, 0, tzinfo=EST)
        result = add_working_hours(start, 2, "America/New_York", "US")
        assert result == datetime(2024, 7, 5, 10, 0, tzinfo=EST)


class TestCalculateDeadline:
    def test_sla_8h_same_day(self):
        start = datetime(2024, 3, 11, 9, 0, tzinfo=EST)
        result = calculate_deadline(start, 8)
        assert result["deadline"] == datetime(2024, 3, 11, 17, 0, tzinfo=EST)

    def test_sla_crosses_day(self):
        start = datetime(2024, 3, 11, 15, 0, tzinfo=EST)
        result = calculate_deadline(start, 8)
        assert result["deadline"] == datetime(2024, 3, 12, 15, 0, tzinfo=EST)

    def test_sla_result_has_required_fields(self):
        start = datetime(2024, 3, 11, 9, 0, tzinfo=EST)
        result = calculate_deadline(start, 24)
        assert "deadline" in result
        assert "business_days_elapsed" in result
        assert "calendar_days_elapsed" in result
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_working_hours_calc.py -v
```
Expected: ImportError.

**Step 3: Implement api/calculators/working_hours.py**

```python
from datetime import datetime, timedelta, time, timezone
from typing import Optional
import zoneinfo
from api.calculators.holidays import get_holidays

WORK_START = time(9, 0)
WORK_END = time(17, 0)
WORK_SECONDS_PER_DAY = 8 * 3600


def _ensure_tz(dt: datetime, tz_name: str) -> datetime:
    tz = zoneinfo.ZoneInfo(tz_name)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz)
    return dt.astimezone(tz)


def _build_holiday_set(start_date, end_date, country, region) -> set:
    if not country:
        return set()
    holidays = set()
    for year in range(start_date.year, end_date.year + 2):
        holidays.update(get_holidays(year, country, region).keys())
    return holidays


def working_hours_between(
    start: datetime, end: datetime,
    timezone_name: str = "UTC",
    country: Optional[str] = None,
    region: Optional[str] = None,
) -> float:
    start = _ensure_tz(start, timezone_name)
    end = _ensure_tz(end, timezone_name)
    if start >= end:
        return 0.0

    tz = zoneinfo.ZoneInfo(timezone_name)
    holiday_set = _build_holiday_set(start.date(), end.date(), country, region)
    total_seconds = 0.0
    current_date = start.date()
    end_date = end.date()

    while current_date <= end_date:
        if current_date.weekday() < 5 and current_date not in holiday_set:
            day_start = datetime.combine(current_date, WORK_START, tzinfo=tz)
            day_end = datetime.combine(current_date, WORK_END, tzinfo=tz)
            period_start = max(start, day_start)
            period_end = min(end, day_end)
            if period_end > period_start:
                total_seconds += (period_end - period_start).total_seconds()
        current_date += timedelta(days=1)

    return round(total_seconds / 3600, 4)


def add_working_hours(
    start: datetime, hours: float,
    timezone_name: str = "UTC",
    country: Optional[str] = None,
    region: Optional[str] = None,
) -> datetime:
    start = _ensure_tz(start, timezone_name)
    tz = zoneinfo.ZoneInfo(timezone_name)
    remaining_seconds = hours * 3600
    current = start
    holiday_cache: dict[int, set] = {}

    while remaining_seconds > 0:
        current_date = current.date()
        year = current_date.year
        if year not in holiday_cache:
            holiday_cache[year] = set(get_holidays(year, country, region).keys()) if country else set()

        if current.weekday() < 5 and current_date not in holiday_cache[year]:
            day_end = datetime.combine(current_date, WORK_END, tzinfo=tz)
            work_start = max(current, datetime.combine(current_date, WORK_START, tzinfo=tz))
            available = max(0.0, (day_end - work_start).total_seconds())
            if available >= remaining_seconds:
                return work_start + timedelta(seconds=remaining_seconds)
            remaining_seconds -= available

        # Advance to next work day start
        next_date = current_date + timedelta(days=1)
        current = datetime.combine(next_date, WORK_START, tzinfo=tz)

    return current


def calculate_deadline(
    start: datetime, sla_hours: float,
    timezone_name: str = "UTC",
    country: Optional[str] = None,
    region: Optional[str] = None,
) -> dict:
    deadline = add_working_hours(start, sla_hours, timezone_name, country, region)
    calendar_days = (deadline.date() - start.date()).days
    # Count business days elapsed
    from api.calculators.business_days import business_days_between
    business_days = business_days_between(start.date(), deadline.date(), country, region)
    return {
        "deadline": deadline,
        "business_days_elapsed": business_days,
        "calendar_days_elapsed": calendar_days,
    }
```

**Step 4: Run tests**

```bash
pytest tests/test_working_hours_calc.py -v
```
Expected: All PASS. Fix any failures.

**Step 5: Commit**

```bash
git add api/calculators/working_hours.py tests/test_working_hours_calc.py
git commit -m "feat: working hours calculator with timezone and holiday awareness"
```

---

## Task 5: Calendar Intelligence Calculator

**Files:**
- Create: `api/calculators/calendar.py`
- Create: `tests/test_calendar_calc.py`

**Step 1: Write failing tests**

Create `tests/test_calendar_calc.py`:
```python
import pytest
from datetime import date
from api.calculators.calendar import (
    week_number, quarter_info, fiscal_year_info,
    month_boundaries, nth_weekday, days_until, date_info,
)


class TestWeekNumber:
    def test_known_week(self):
        result = week_number(date(2024, 3, 11))
        assert result["iso_week"] == 11
        assert result["iso_year"] == 2024

    def test_week_1_jan(self):
        result = week_number(date(2025, 1, 1))
        assert result["iso_week"] == 1

    def test_year_boundary_week(self):
        # Dec 30 2024 is ISO week 1 of 2025
        result = week_number(date(2024, 12, 30))
        assert result["iso_year"] == 2025
        assert result["iso_week"] == 1


class TestQuarterInfo:
    def test_q1(self):
        result = quarter_info(date(2024, 2, 15))
        assert result["quarter"] == 1
        assert result["quarter_start"] == date(2024, 1, 1)
        assert result["quarter_end"] == date(2024, 3, 31)

    def test_q2(self):
        result = quarter_info(date(2024, 5, 1))
        assert result["quarter"] == 2

    def test_q3(self):
        result = quarter_info(date(2024, 8, 31))
        assert result["quarter"] == 3

    def test_q4(self):
        result = quarter_info(date(2024, 12, 31))
        assert result["quarter"] == 4

    def test_days_remaining_in_quarter(self):
        result = quarter_info(date(2024, 3, 31))
        assert result["days_remaining_in_quarter"] == 0


class TestFiscalYearInfo:
    def test_calendar_fiscal_year_jan(self):
        result = fiscal_year_info(date(2024, 6, 15), fiscal_start_month=1)
        assert result["fiscal_year"] == 2024

    def test_fiscal_year_april_start(self):
        # UK fiscal year starts April 1
        result = fiscal_year_info(date(2024, 6, 15), fiscal_start_month=4)
        assert result["fiscal_year"] == 2025  # FY2025 runs Apr 2024 - Mar 2025

    def test_fiscal_year_october_start(self):
        # US federal fiscal year starts Oct 1
        result = fiscal_year_info(date(2024, 11, 1), fiscal_start_month=10)
        assert result["fiscal_year"] == 2025

    def test_fiscal_year_has_required_fields(self):
        result = fiscal_year_info(date(2024, 3, 11))
        assert "fiscal_year" in result
        assert "fiscal_year_start" in result
        assert "fiscal_year_end" in result
        assert "days_elapsed" in result
        assert "days_remaining" in result


class TestMonthBoundaries:
    def test_january_boundaries(self):
        result = month_boundaries(2024, 1)
        assert result["first_calendar_day"] == date(2024, 1, 1)
        assert result["last_calendar_day"] == date(2024, 1, 31)

    def test_first_business_day_jan_2024(self):
        # Jan 1 2024 is Monday but it's a holiday; Jan 2 is first biz day
        result = month_boundaries(2024, 1, "US")
        assert result["first_business_day"] == date(2024, 1, 2)

    def test_last_business_day_dec_2024(self):
        # Dec 31 2024 is Tuesday
        result = month_boundaries(2024, 12, "US")
        assert result["last_business_day"] == date(2024, 12, 31)

    def test_february_leap_year(self):
        result = month_boundaries(2024, 2)
        assert result["last_calendar_day"] == date(2024, 2, 29)

    def test_february_non_leap_year(self):
        result = month_boundaries(2023, 2)
        assert result["last_calendar_day"] == date(2023, 2, 28)


class TestNthWeekday:
    def test_first_monday_march_2026(self):
        assert nth_weekday(2026, 3, 1, 0) == date(2026, 3, 2)  # n=1, weekday=Mon=0

    def test_third_monday_march_2026(self):
        assert nth_weekday(2026, 3, 3, 0) == date(2026, 3, 16)

    def test_last_friday(self):
        # Last Friday of March 2026
        assert nth_weekday(2026, 3, -1, 4) == date(2026, 3, 27)

    def test_fifth_monday_may_2026(self):
        # May 2026: Mondays are 4, 11, 18, 25 — no 5th Monday
        with pytest.raises(ValueError):
            nth_weekday(2026, 5, 5, 0)


class TestDaysUntil:
    def test_days_until_end_of_week(self):
        result = days_until(date(2024, 3, 11))  # Monday
        assert result["end_of_week"] == 4  # Mon to Sun = 6 - 0 = 6 days, but end_of_week is Sunday

    def test_days_until_end_of_month(self):
        result = days_until(date(2024, 3, 11))
        assert result["end_of_month"] == 20  # 31 - 11 = 20

    def test_days_until_end_of_year(self):
        result = days_until(date(2024, 12, 1))
        assert result["end_of_year"] == 30


class TestDateInfo:
    def test_returns_all_fields(self):
        result = date_info(date(2024, 3, 11), "US")
        assert "date" in result
        assert "day_of_week" in result
        assert "is_weekend" in result
        assert "is_business_day" in result
        assert "is_holiday" in result
        assert "holiday_name" in result
        assert "iso_week" in result
        assert "iso_year" in result
        assert "quarter" in result
        assert "fiscal_year" in result
        assert "days_until_end_of_month" in result
        assert "days_until_end_of_quarter" in result
        assert "days_until_end_of_year" in result

    def test_christmas_is_holiday(self):
        result = date_info(date(2024, 12, 25), "US")
        assert result["is_holiday"] is True
        assert result["is_business_day"] is False
        assert "Christmas" in result["holiday_name"]
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_calendar_calc.py -v
```
Expected: ImportError.

**Step 3: Implement api/calculators/calendar.py**

```python
from datetime import date, timedelta
from typing import Optional
import calendar
from api.calculators.holidays import get_holidays, is_holiday as _is_holiday
from api.calculators.business_days import is_business_day, next_business_day, previous_business_day

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
QUARTER_MONTHS = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 10: 4, 11: 4, 12: 4}
QUARTER_START_MONTH = {1: 1, 2: 4, 3: 7, 4: 10}
QUARTER_END_MONTH = {1: 3, 2: 6, 3: 9, 4: 12}


def week_number(d: date) -> dict:
    iso = d.isocalendar()
    return {
        "iso_week": iso.week,
        "iso_year": iso.year,
        "week_start": d - timedelta(days=d.weekday()),
        "week_end": d + timedelta(days=6 - d.weekday()),
    }


def quarter_info(d: date) -> dict:
    q = QUARTER_MONTHS[d.month]
    q_start_month = QUARTER_START_MONTH[q]
    q_end_month = QUARTER_END_MONTH[q]
    q_start = date(d.year, q_start_month, 1)
    last_day = calendar.monthrange(d.year, q_end_month)[1]
    q_end = date(d.year, q_end_month, last_day)
    return {
        "quarter": q,
        "quarter_start": q_start,
        "quarter_end": q_end,
        "days_elapsed_in_quarter": (d - q_start).days,
        "days_remaining_in_quarter": (q_end - d).days,
        "total_days_in_quarter": (q_end - q_start).days + 1,
    }


def fiscal_year_info(d: date, fiscal_start_month: int = 1) -> dict:
    if d.month >= fiscal_start_month:
        fy_start_year = d.year
    else:
        fy_start_year = d.year - 1

    fy_start = date(fy_start_year, fiscal_start_month, 1)
    # Fiscal year end is last day of month before fiscal_start_month next year
    fy_end_year = fy_start_year + 1
    fy_end_month = fiscal_start_month - 1 if fiscal_start_month > 1 else 12
    if fiscal_start_month == 1:
        fy_end_year = fy_start_year
        fy_end_month = 12
    last_day = calendar.monthrange(fy_end_year, fy_end_month)[1]
    fy_end = date(fy_end_year, fy_end_month, last_day)

    fiscal_year = fy_start_year + 1 if fiscal_start_month > 1 else fy_start_year

    return {
        "fiscal_year": fiscal_year,
        "fiscal_start_month": fiscal_start_month,
        "fiscal_year_start": fy_start,
        "fiscal_year_end": fy_end,
        "days_elapsed": (d - fy_start).days,
        "days_remaining": (fy_end - d).days,
        "total_days": (fy_end - fy_start).days + 1,
    }


def month_boundaries(
    year: int, month: int,
    country: Optional[str] = None, region: Optional[str] = None
) -> dict:
    first_day = date(year, month, 1)
    last_day_num = calendar.monthrange(year, month)[1]
    last_day = date(year, month, last_day_num)

    result = {
        "year": year,
        "month": month,
        "first_calendar_day": first_day,
        "last_calendar_day": last_day,
        "total_calendar_days": last_day_num,
    }

    if country:
        first_biz = first_day if is_business_day(first_day, country, region) else next_business_day(first_day, country, region)
        last_biz = last_day if is_business_day(last_day, country, region) else previous_business_day(last_day, country, region)
        result["first_business_day"] = first_biz
        result["last_business_day"] = last_biz

    return result


def nth_weekday(year: int, month: int, n: int, weekday: int) -> date:
    """
    Return the nth occurrence of weekday (0=Mon..6=Sun) in a given month.
    n=-1 means last occurrence.
    Raises ValueError if n exceeds occurrences in the month.
    """
    if n == -1:
        last_day = calendar.monthrange(year, month)[1]
        d = date(year, month, last_day)
        while d.weekday() != weekday:
            d -= timedelta(days=1)
        return d

    if n < 1:
        raise ValueError("n must be >= 1 or -1 for last")

    # Find first occurrence
    first = date(year, month, 1)
    days_ahead = weekday - first.weekday()
    if days_ahead < 0:
        days_ahead += 7
    first_occurrence = first + timedelta(days=days_ahead)
    result = first_occurrence + timedelta(weeks=n - 1)
    if result.month != month:
        raise ValueError(f"No {n}th weekday {weekday} in {year}-{month:02d}")
    return result


def days_until(d: date) -> dict:
    # End of week (Sunday)
    end_of_week = d + timedelta(days=6 - d.weekday())
    # End of month
    last_day_num = calendar.monthrange(d.year, d.month)[1]
    end_of_month = date(d.year, d.month, last_day_num)
    # End of quarter
    q_info = quarter_info(d)
    end_of_quarter = q_info["quarter_end"]
    # End of year
    end_of_year = date(d.year, 12, 31)
    return {
        "end_of_week": (end_of_week - d).days,
        "end_of_month": (end_of_month - d).days,
        "end_of_quarter": (end_of_quarter - d).days,
        "end_of_year": (end_of_year - d).days,
    }


def date_info(
    d: date,
    country: Optional[str] = None,
    region: Optional[str] = None,
    fiscal_start_month: int = 1,
) -> dict:
    h = get_holidays(d.year, country, region) if country else {}
    holiday = h.get(d)
    q = quarter_info(d)
    fy = fiscal_year_info(d, fiscal_start_month)
    w = week_number(d)
    du = days_until(d)
    return {
        "date": d.isoformat(),
        "day_of_week": WEEKDAY_NAMES[d.weekday()],
        "day_of_week_number": d.weekday(),
        "day_of_month": d.day,
        "day_of_year": d.timetuple().tm_yday,
        "is_weekend": d.weekday() >= 5,
        "is_business_day": is_business_day(d, country, region),
        "is_holiday": holiday is not None,
        "holiday_name": holiday or None,
        "iso_week": w["iso_week"],
        "iso_year": w["iso_year"],
        "week_start": w["week_start"].isoformat(),
        "week_end": w["week_end"].isoformat(),
        "quarter": q["quarter"],
        "quarter_start": q["quarter_start"].isoformat(),
        "quarter_end": q["quarter_end"].isoformat(),
        "days_elapsed_in_quarter": q["days_elapsed_in_quarter"],
        "days_remaining_in_quarter": q["days_remaining_in_quarter"],
        "fiscal_year": fy["fiscal_year"],
        "fiscal_year_start": fy["fiscal_year_start"].isoformat(),
        "fiscal_year_end": fy["fiscal_year_end"].isoformat(),
        "days_until_end_of_week": du["end_of_week"],
        "days_until_end_of_month": du["end_of_month"],
        "days_until_end_of_quarter": du["end_of_quarter"],
        "days_until_end_of_year": du["end_of_year"],
        "country": country,
        "region": region,
    }
```

**Step 4: Run tests**

```bash
pytest tests/test_calendar_calc.py -v
```
Expected: All PASS. Fix any failures.

**Step 5: Commit**

```bash
git add api/calculators/calendar.py tests/test_calendar_calc.py
git commit -m "feat: calendar intelligence calculator (quarters, fiscal year, nth weekday, date-info)"
```

---

## Task 6: Business Days Routes

**Files:**
- Modify: `api/routes/business_days.py`
- Create: `tests/test_business_days_routes.py`

**Step 1: Write failing route tests**

Create `tests/test_business_days_routes.py`:
```python
def test_between(client):
    r = client.get("/business-days/between?start=2024-03-11&end=2024-03-18")
    assert r.status_code == 200
    assert r.json()["business_days"] == 5

def test_between_with_country(client):
    r = client.get("/business-days/between?start=2024-07-01&end=2024-07-08&country=US")
    assert r.json()["business_days"] == 4  # July 4 excluded

def test_add(client):
    r = client.get("/business-days/add?date=2024-03-15&days=1")
    assert r.json()["result_date"] == "2024-03-18"

def test_subtract(client):
    r = client.get("/business-days/subtract?date=2024-03-18&days=1")
    assert r.json()["result_date"] == "2024-03-15"

def test_next(client):
    r = client.get("/business-days/next?date=2024-03-15")
    assert r.json()["next_business_day"] == "2024-03-18"

def test_previous(client):
    r = client.get("/business-days/previous?date=2024-03-18")
    assert r.json()["previous_business_day"] == "2024-03-15"

def test_is_business_day_true(client):
    r = client.get("/business-days/is-business-day?date=2024-03-11")
    assert r.json()["is_business_day"] is True

def test_is_business_day_saturday(client):
    r = client.get("/business-days/is-business-day?date=2024-03-09")
    assert r.json()["is_business_day"] is False

def test_invalid_date_returns_422(client):
    r = client.get("/business-days/between?start=not-a-date&end=2024-03-18")
    assert r.status_code == 422

def test_invalid_country_returns_400(client):
    r = client.get("/business-days/between?start=2024-03-11&end=2024-03-18&country=XX")
    assert r.status_code == 400
```

**Step 2: Run to verify they fail**

```bash
pytest tests/test_business_days_routes.py -v
```
Expected: 404 errors (routes not implemented).

**Step 3: Implement api/routes/business_days.py**

```python
from fastapi import APIRouter, Query, HTTPException
from datetime import date
from typing import Optional
from api.calculators.business_days import (
    is_business_day, business_days_between,
    add_business_days, subtract_business_days,
    next_business_day, previous_business_day,
)
from api.calculators.holidays import SUPPORTED_COUNTRIES

router = APIRouter()


def _validate_country(country: Optional[str], region: Optional[str]) -> None:
    if country and country not in SUPPORTED_COUNTRIES:
        raise HTTPException(status_code=400, detail=f"Unsupported country: {country}. See /holidays/countries.")
    if country and region and region not in SUPPORTED_COUNTRIES.get(country, {}).get("regions", {}):
        raise HTTPException(status_code=400, detail=f"Unsupported region '{region}' for country '{country}'.")


@router.get("/between")
def between(
    start: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end: date = Query(..., description="End date (YYYY-MM-DD)"),
    country: Optional[str] = Query(None, description="ISO country code (e.g. US, GB)"),
    region: Optional[str] = Query(None, description="Sub-national region code (e.g. TX, ENG)"),
):
    _validate_country(country, region)
    count = business_days_between(start, end, country, region)
    return {"start": start, "end": end, "business_days": count, "country": country, "region": region}


@router.get("/add")
def add(
    date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    days: int = Query(..., ge=0, description="Number of business days to add"),
    country: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
):
    _validate_country(country, region)
    result = add_business_days(date, days, country, region)
    return {"start_date": date, "days_added": days, "result_date": result, "country": country, "region": region}


@router.get("/subtract")
def subtract(
    date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    days: int = Query(..., ge=0, description="Number of business days to subtract"),
    country: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
):
    _validate_country(country, region)
    result = subtract_business_days(date, days, country, region)
    return {"start_date": date, "days_subtracted": days, "result_date": result, "country": country, "region": region}


@router.get("/next")
def next(
    date: date = Query(...),
    country: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
):
    _validate_country(country, region)
    result = next_business_day(date, country, region)
    return {"from_date": date, "next_business_day": result, "country": country, "region": region}


@router.get("/previous")
def previous(
    date: date = Query(...),
    country: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
):
    _validate_country(country, region)
    result = previous_business_day(date, country, region)
    return {"from_date": date, "previous_business_day": result, "country": country, "region": region}


@router.get("/is-business-day")
def check_is_business_day(
    date: date = Query(...),
    country: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
):
    _validate_country(country, region)
    result = is_business_day(date, country, region)
    return {"date": date, "is_business_day": result, "country": country, "region": region}
```

**Step 4: Run tests**

```bash
pytest tests/test_business_days_routes.py -v
```
Expected: All PASS.

**Step 5: Commit**

```bash
git add api/routes/business_days.py tests/test_business_days_routes.py
git commit -m "feat: business days HTTP routes (6 endpoints)"
```

---

## Task 7: Working Hours Routes

**Files:**
- Modify: `api/routes/working_hours.py`
- Create: `tests/test_working_hours_routes.py`

**Step 1: Write failing route tests**

Create `tests/test_working_hours_routes.py`:
```python
def test_between(client):
    r = client.get("/working-hours/between?start=2024-03-11T09:00:00&end=2024-03-11T17:00:00&timezone=America/New_York")
    assert r.status_code == 200
    assert r.json()["working_hours"] == 8.0

def test_between_default_utc(client):
    r = client.get("/working-hours/between?start=2024-03-11T09:00:00&end=2024-03-11T13:00:00")
    assert r.json()["working_hours"] == 4.0

def test_add_hours(client):
    r = client.get("/working-hours/add?start=2024-03-15T16:00:00&hours=2&timezone=America/New_York")
    assert r.status_code == 200
    data = r.json()
    assert "result_datetime" in data

def test_deadline(client):
    r = client.get("/working-hours/deadline?start=2024-03-11T09:00:00&sla_hours=8&timezone=America/New_York")
    assert r.status_code == 200
    data = r.json()
    assert "deadline" in data
    assert "business_days_elapsed" in data
    assert "calendar_days_elapsed" in data

def test_invalid_timezone_returns_400(client):
    r = client.get("/working-hours/between?start=2024-03-11T09:00:00&end=2024-03-11T17:00:00&timezone=Invalid/Zone")
    assert r.status_code == 400

def test_sla_hours_must_be_positive(client):
    r = client.get("/working-hours/deadline?start=2024-03-11T09:00:00&sla_hours=-1")
    assert r.status_code == 422
```

**Step 2: Run to verify they fail**

```bash
pytest tests/test_working_hours_routes.py -v
```

**Step 3: Implement api/routes/working_hours.py**

```python
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from typing import Optional
import zoneinfo
from api.calculators.working_hours import working_hours_between, add_working_hours, calculate_deadline
from api.calculators.holidays import SUPPORTED_COUNTRIES

router = APIRouter()


def _validate_timezone(tz_name: str) -> None:
    try:
        zoneinfo.ZoneInfo(tz_name)
    except (zoneinfo.ZoneInfoNotFoundError, KeyError):
        raise HTTPException(status_code=400, detail=f"Invalid timezone: '{tz_name}'. Use IANA format e.g. America/New_York.")


def _validate_country(country: Optional[str], region: Optional[str]) -> None:
    if country and country not in SUPPORTED_COUNTRIES:
        raise HTTPException(status_code=400, detail=f"Unsupported country: {country}.")
    if country and region and region not in SUPPORTED_COUNTRIES.get(country, {}).get("regions", {}):
        raise HTTPException(status_code=400, detail=f"Unsupported region '{region}' for country '{country}'.")


@router.get("/between")
def between(
    start: datetime = Query(..., description="Start datetime (ISO 8601, e.g. 2024-03-11T09:00:00)"),
    end: datetime = Query(..., description="End datetime (ISO 8601)"),
    timezone: str = Query("UTC", description="IANA timezone string (e.g. America/New_York)"),
    country: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
):
    _validate_timezone(timezone)
    _validate_country(country, region)
    hours = working_hours_between(start, end, timezone, country, region)
    return {"start": start, "end": end, "working_hours": hours, "timezone": timezone, "country": country, "region": region}


@router.get("/add")
def add(
    start: datetime = Query(...),
    hours: float = Query(..., gt=0, description="Working hours to add"),
    timezone: str = Query("UTC"),
    country: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
):
    _validate_timezone(timezone)
    _validate_country(country, region)
    result = add_working_hours(start, hours, timezone, country, region)
    return {"start": start, "hours_added": hours, "result_datetime": result, "timezone": timezone}


@router.get("/deadline")
def deadline(
    start: datetime = Query(..., description="SLA start datetime"),
    sla_hours: float = Query(..., gt=0, description="SLA duration in working hours"),
    timezone: str = Query("UTC"),
    country: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
):
    _validate_timezone(timezone)
    _validate_country(country, region)
    result = calculate_deadline(start, sla_hours, timezone, country, region)
    return {
        "start": start,
        "sla_hours": sla_hours,
        "deadline": result["deadline"],
        "business_days_elapsed": result["business_days_elapsed"],
        "calendar_days_elapsed": result["calendar_days_elapsed"],
        "timezone": timezone,
        "country": country,
        "region": region,
    }
```

**Step 4: Run tests**

```bash
pytest tests/test_working_hours_routes.py -v
```
Expected: All PASS.

**Step 5: Commit**

```bash
git add api/routes/working_hours.py tests/test_working_hours_routes.py
git commit -m "feat: working hours HTTP routes (3 endpoints)"
```

---

## Task 8: Holiday Routes

**Files:**
- Modify: `api/routes/holidays.py`
- Create: `tests/test_holidays_routes.py`

**Step 1: Write failing route tests**

Create `tests/test_holidays_routes.py`:
```python
def test_list_us_holidays(client):
    r = client.get("/holidays/list?country=US&year=2024")
    assert r.status_code == 200
    data = r.json()
    assert "holidays" in data
    assert len(data["holidays"]) > 0
    assert "date" in data["holidays"][0]
    assert "name" in data["holidays"][0]

def test_list_with_region(client):
    r = client.get("/holidays/list?country=GB&year=2024&region=SCT")
    assert r.status_code == 200

def test_is_holiday_true(client):
    r = client.get("/holidays/is-holiday?date=2024-12-25&country=US")
    assert r.json()["is_holiday"] is True

def test_is_holiday_false(client):
    r = client.get("/holidays/is-holiday?date=2024-03-15&country=US")
    assert r.json()["is_holiday"] is False

def test_next_holiday(client):
    r = client.get("/holidays/next?date=2024-12-24&country=US")
    assert r.status_code == 200
    data = r.json()
    assert data["next_holiday"]["date"] == "2024-12-25"

def test_countries(client):
    r = client.get("/holidays/countries")
    assert r.status_code == 200
    data = r.json()
    assert "countries" in data
    assert len(data["countries"]) == 15

def test_invalid_country_returns_400(client):
    r = client.get("/holidays/list?country=XX&year=2024")
    assert r.status_code == 400
```

**Step 2: Run to verify they fail**

```bash
pytest tests/test_holidays_routes.py -v
```

**Step 3: Implement api/routes/holidays.py**

```python
from fastapi import APIRouter, Query, HTTPException
from datetime import date
from typing import Optional
from api.calculators.holidays import (
    get_holidays, is_holiday, list_holidays, next_holiday, supported_countries,
    SUPPORTED_COUNTRIES,
)

router = APIRouter()


def _validate_country(country: str, region: Optional[str] = None) -> None:
    if country not in SUPPORTED_COUNTRIES:
        raise HTTPException(status_code=400, detail=f"Unsupported country: '{country}'. See /holidays/countries.")
    if region and region not in SUPPORTED_COUNTRIES[country].get("regions", {}):
        raise HTTPException(status_code=400, detail=f"Unsupported region '{region}' for country '{country}'.")


@router.get("/list")
def list_endpoint(
    country: str = Query(..., description="ISO country code"),
    year: int = Query(..., ge=1900, le=2100, description="Year"),
    region: Optional[str] = Query(None, description="Sub-national region code"),
):
    _validate_country(country, region)
    holidays = list_holidays(year, country, region)
    return {
        "country": country,
        "region": region,
        "year": year,
        "count": len(holidays),
        "holidays": [{"date": h["date"].isoformat(), "name": h["name"]} for h in holidays],
    }


@router.get("/is-holiday")
def is_holiday_endpoint(
    date: date = Query(...),
    country: str = Query(...),
    region: Optional[str] = Query(None),
):
    _validate_country(country, region)
    h = get_holidays(date.year, country, region)
    holiday_name = h.get(date)
    return {
        "date": date,
        "country": country,
        "region": region,
        "is_holiday": holiday_name is not None,
        "holiday_name": holiday_name or None,
    }


@router.get("/next")
def next_endpoint(
    date: date = Query(...),
    country: str = Query(...),
    region: Optional[str] = Query(None),
):
    _validate_country(country, region)
    result = next_holiday(date, country, region)
    if not result:
        raise HTTPException(status_code=404, detail="No upcoming holidays found in the next 3 years.")
    return {
        "from_date": date,
        "country": country,
        "region": region,
        "next_holiday": {"date": result["date"].isoformat(), "name": result["name"]},
    }


@router.get("/countries")
def countries_endpoint():
    sc = supported_countries()
    return {
        "count": len(sc),
        "countries": [
            {
                "code": code,
                "name": info["name"],
                "region_count": len(info["regions"]),
                "regions": info["regions"],
            }
            for code, info in sc.items()
        ],
    }
```

**Step 4: Run tests**

```bash
pytest tests/test_holidays_routes.py -v
```
Expected: All PASS.

**Step 5: Commit**

```bash
git add api/routes/holidays.py tests/test_holidays_routes.py
git commit -m "feat: holiday HTTP routes (4 endpoints)"
```

---

## Task 9: Calendar Routes

**Files:**
- Modify: `api/routes/calendar.py`
- Create: `tests/test_calendar_routes.py`

**Step 1: Write failing route tests**

Create `tests/test_calendar_routes.py`:
```python
def test_week_number(client):
    r = client.get("/calendar/week-number?date=2024-03-11")
    assert r.status_code == 200
    assert r.json()["iso_week"] == 11

def test_quarter(client):
    r = client.get("/calendar/quarter?date=2024-02-15")
    assert r.json()["quarter"] == 1

def test_fiscal_year_default(client):
    r = client.get("/calendar/fiscal-year?date=2024-06-15")
    assert r.status_code == 200
    assert "fiscal_year" in r.json()

def test_fiscal_year_custom_start(client):
    r = client.get("/calendar/fiscal-year?date=2024-06-15&fiscal_start_month=4")
    assert r.json()["fiscal_year"] == 2025

def test_month_boundaries(client):
    r = client.get("/calendar/month-boundaries?year=2024&month=2")
    data = r.json()
    assert data["last_calendar_day"] == "2024-02-29"  # leap year

def test_nth_weekday(client):
    r = client.get("/calendar/nth-weekday?year=2026&month=3&n=1&weekday=0")
    assert r.json()["date"] == "2026-03-02"

def test_nth_weekday_invalid(client):
    r = client.get("/calendar/nth-weekday?year=2026&month=5&n=5&weekday=0")
    assert r.status_code == 400

def test_days_until(client):
    r = client.get("/calendar/days-until?date=2024-03-11")
    assert r.status_code == 200
    data = r.json()
    assert "end_of_week" in data
    assert "end_of_month" in data
    assert "end_of_quarter" in data
    assert "end_of_year" in data

def test_date_info(client):
    r = client.get("/calendar/date-info?date=2024-12-25&country=US")
    data = r.json()
    assert data["is_holiday"] is True
    assert "Christmas" in data["holiday_name"]
    assert data["is_business_day"] is False

def test_date_info_no_country(client):
    r = client.get("/calendar/date-info?date=2024-03-11")
    assert r.status_code == 200
```

**Step 2: Run to verify they fail**

```bash
pytest tests/test_calendar_routes.py -v
```

**Step 3: Implement api/routes/calendar.py**

```python
from fastapi import APIRouter, Query, HTTPException
from datetime import date
from typing import Optional
from api.calculators.calendar import (
    week_number, quarter_info, fiscal_year_info,
    month_boundaries, nth_weekday, days_until, date_info,
)
from api.calculators.holidays import SUPPORTED_COUNTRIES

router = APIRouter()


def _validate_country(country: Optional[str], region: Optional[str] = None) -> None:
    if country and country not in SUPPORTED_COUNTRIES:
        raise HTTPException(status_code=400, detail=f"Unsupported country: '{country}'.")
    if country and region and region not in SUPPORTED_COUNTRIES[country].get("regions", {}):
        raise HTTPException(status_code=400, detail=f"Unsupported region '{region}' for '{country}'.")


@router.get("/week-number")
def week_number_endpoint(date: date = Query(...)):
    result = week_number(date)
    return {
        "date": date,
        "iso_week": result["iso_week"],
        "iso_year": result["iso_year"],
        "week_start": result["week_start"],
        "week_end": result["week_end"],
    }


@router.get("/quarter")
def quarter_endpoint(date: date = Query(...)):
    result = quarter_info(date)
    return {"date": date, **result}


@router.get("/fiscal-year")
def fiscal_year_endpoint(
    date: date = Query(...),
    fiscal_start_month: int = Query(1, ge=1, le=12, description="Month fiscal year starts (1=Jan, 4=Apr, 10=Oct)"),
):
    result = fiscal_year_info(date, fiscal_start_month)
    return {"date": date, **result}


@router.get("/month-boundaries")
def month_boundaries_endpoint(
    year: int = Query(..., ge=1900, le=2100),
    month: int = Query(..., ge=1, le=12),
    country: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
):
    _validate_country(country, region)
    result = month_boundaries(year, month, country, region)
    return result


@router.get("/nth-weekday")
def nth_weekday_endpoint(
    year: int = Query(..., ge=1900, le=2100),
    month: int = Query(..., ge=1, le=12),
    n: int = Query(..., description="Nth occurrence (1-5) or -1 for last"),
    weekday: int = Query(..., ge=0, le=6, description="Weekday: 0=Monday, 6=Sunday"),
):
    try:
        result = nth_weekday(year, month, n, weekday)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return {
        "year": year, "month": month, "n": n,
        "weekday": weekday, "weekday_name": weekday_names[weekday],
        "date": result,
    }


@router.get("/days-until")
def days_until_endpoint(date: date = Query(...)):
    result = days_until(date)
    return {"date": date, **result}


@router.get("/date-info")
def date_info_endpoint(
    date: date = Query(...),
    country: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    fiscal_start_month: int = Query(1, ge=1, le=12),
):
    _validate_country(country, region)
    return date_info(date, country, region, fiscal_start_month)
```

**Step 4: Run tests**

```bash
pytest tests/test_calendar_routes.py -v
```
Expected: All PASS.

**Step 5: Commit**

```bash
git add api/routes/calendar.py tests/test_calendar_routes.py
git commit -m "feat: calendar intelligence HTTP routes (8 endpoints)"
```

---

## Task 10: Bulk Endpoint (Pro)

**Files:**
- Modify: `api/routes/bulk.py`
- Create: `tests/test_bulk_routes.py`

**Step 1: Write failing tests**

Create `tests/test_bulk_routes.py`:
```python
def test_bulk_business_days_between(client):
    payload = {
        "requests": [
            {"endpoint": "business-days/between", "params": {"start": "2024-03-11", "end": "2024-03-18"}},
            {"endpoint": "business-days/between", "params": {"start": "2024-07-01", "end": "2024-07-08", "country": "US"}},
        ]
    }
    r = client.post("/bulk", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert len(data["results"]) == 2
    assert data["results"][0]["business_days"] == 5
    assert data["results"][1]["business_days"] == 4

def test_bulk_max_50(client):
    payload = {
        "requests": [
            {"endpoint": "business-days/is-business-day", "params": {"date": "2024-03-11"}}
            for _ in range(51)
        ]
    }
    r = client.post("/bulk", json=payload)
    assert r.status_code == 422

def test_bulk_empty_returns_400(client):
    r = client.post("/bulk", json={"requests": []})
    assert r.status_code == 422

def test_bulk_mixed_endpoints(client):
    payload = {
        "requests": [
            {"endpoint": "business-days/next", "params": {"date": "2024-03-15"}},
            {"endpoint": "calendar/week-number", "params": {"date": "2024-03-11"}},
            {"endpoint": "holidays/is-holiday", "params": {"date": "2024-12-25", "country": "US"}},
        ]
    }
    r = client.post("/bulk", json=payload)
    assert r.status_code == 200
    assert len(r.json()["results"]) == 3
```

**Step 2: Run to verify they fail**

```bash
pytest tests/test_bulk_routes.py -v
```

**Step 3: Implement api/routes/bulk.py**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any
from datetime import date, datetime
from api.calculators.business_days import (
    is_business_day, business_days_between, add_business_days,
    subtract_business_days, next_business_day, previous_business_day,
)
from api.calculators.working_hours import working_hours_between, add_working_hours, calculate_deadline
from api.calculators.holidays import get_holidays, is_holiday, list_holidays, next_holiday
from api.calculators.calendar import week_number, quarter_info, fiscal_year_info, month_boundaries, nth_weekday, days_until, date_info

router = APIRouter()


class BulkRequest(BaseModel):
    endpoint: str
    params: dict[str, Any]


class BulkPayload(BaseModel):
    requests: list[BulkRequest] = Field(..., min_length=1, max_length=50)


def _parse_date(val: Any) -> date:
    if isinstance(val, date):
        return val
    return date.fromisoformat(str(val))


def _dispatch(endpoint: str, params: dict) -> Any:
    """Route a single bulk request to the appropriate calculator function."""
    try:
        if endpoint == "business-days/between":
            return business_days_between(
                _parse_date(params["start"]), _parse_date(params["end"]),
                params.get("country"), params.get("region")
            )
        elif endpoint == "business-days/add":
            return add_business_days(_parse_date(params["date"]), int(params["days"]), params.get("country"), params.get("region"))
        elif endpoint == "business-days/subtract":
            return subtract_business_days(_parse_date(params["date"]), int(params["days"]), params.get("country"), params.get("region"))
        elif endpoint == "business-days/next":
            return next_business_day(_parse_date(params["date"]), params.get("country"), params.get("region"))
        elif endpoint == "business-days/previous":
            return previous_business_day(_parse_date(params["date"]), params.get("country"), params.get("region"))
        elif endpoint == "business-days/is-business-day":
            return is_business_day(_parse_date(params["date"]), params.get("country"), params.get("region"))
        elif endpoint == "calendar/week-number":
            return week_number(_parse_date(params["date"]))
        elif endpoint == "calendar/quarter":
            return quarter_info(_parse_date(params["date"]))
        elif endpoint == "calendar/fiscal-year":
            return fiscal_year_info(_parse_date(params["date"]), int(params.get("fiscal_start_month", 1)))
        elif endpoint == "calendar/days-until":
            return days_until(_parse_date(params["date"]))
        elif endpoint == "calendar/date-info":
            return date_info(_parse_date(params["date"]), params.get("country"), params.get("region"), int(params.get("fiscal_start_month", 1)))
        elif endpoint == "holidays/is-holiday":
            h = get_holidays(_parse_date(params["date"]).year, params["country"], params.get("region"))
            d = _parse_date(params["date"])
            return {"is_holiday": d in h, "holiday_name": h.get(d)}
        elif endpoint == "holidays/list":
            return list_holidays(int(params["year"]), params["country"], params.get("region"))
        elif endpoint == "holidays/next":
            return next_holiday(_parse_date(params["date"]), params["country"], params.get("region"))
        else:
            return {"error": f"Unknown endpoint: {endpoint}"}
    except (KeyError, ValueError) as e:
        return {"error": str(e)}


def _serialize(value: Any) -> Any:
    """Make calculator results JSON-serializable."""
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize(i) for i in value]
    return value


@router.post("/bulk")
def bulk(payload: BulkPayload):
    results = []
    for req in payload.requests:
        result = _dispatch(req.endpoint, req.params)
        results.append(_serialize(result))
    return {"count": len(results), "results": results}
```

**Step 4: Run tests**

```bash
pytest tests/test_bulk_routes.py -v
```
Expected: All PASS.

**Step 5: Commit**

```bash
git add api/routes/bulk.py tests/test_bulk_routes.py
git commit -m "feat: bulk endpoint (Pro) — batch up to 50 calculations per request"
```

---

## Task 11: Full Test Suite Run

**Step 1: Run all tests**

```bash
pytest tests/ -v --tb=short
```
Expected: All tests PASS. Count should be ~50+.

**Step 2: Fix any failures before continuing.**

**Step 3: Check test coverage**

```bash
pytest tests/ --cov=api --cov-report=term-missing
```
Expected: >85% coverage.

**Step 4: Commit if any fixes were needed**

```bash
git add -A
git commit -m "fix: resolve any test failures, ensure full suite passes"
```

---

## Task 12: Docker & Deployment Setup

**Files:**
- Create: `docker/Dockerfile`
- Create: `docker/nginx.conf`
- Create: `docker-compose.yml`
- Create: `deploy.sh`
- Create: `.dockerignore`
- Create: `.gitignore`

**Step 1: Create docker/Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 2: Create docker/nginx.conf**

```nginx
events {}

http {
    server {
        listen 80;
        server_name _;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://$host$request_uri;
        }
    }

    server {
        listen 443 ssl;
        server_name DOMAIN_PLACEHOLDER;

        ssl_certificate /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/privkey.pem;

        location / {
            proxy_pass http://api:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

**Step 3: Create docker-compose.yml**

```yaml
version: "3.9"

services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    restart: unless-stopped
    networks:
      - bizcal

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - /var/www/certbot:/var/www/certbot:ro
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - bizcal

networks:
  bizcal:
    driver: bridge
```

**Step 4: Create deploy.sh**

```bash
#!/bin/bash
set -e

DOMAIN=${DOMAIN:-"bizcalapi.com"}
EMAIL=${EMAIL:-"your@email.com"}

echo "==> Installing dependencies"
apt-get update -q
apt-get install -y -q docker.io docker-compose

# Install Docker CE if docker.io not available
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
fi

echo "==> Cloning repo"
if [ ! -d "/opt/bizcal" ]; then
    git clone https://github.com/YOUR_GITHUB_USERNAME/bizcal-api /opt/bizcal
fi
cd /opt/bizcal

echo "==> Pulling latest"
git pull

echo "==> Patching nginx domain"
sed -i "s/DOMAIN_PLACEHOLDER/${DOMAIN}/g" docker/nginx.conf

echo "==> Starting HTTP only (for certbot)"
docker-compose up -d nginx

echo "==> Obtaining SSL certificate"
snap install --classic certbot 2>/dev/null || true
certbot certonly --webroot -w /var/www/certbot -d "${DOMAIN}" --email "${EMAIL}" --agree-tos --non-interactive

echo "==> Starting full stack"
docker-compose up -d --build

echo "==> Done. Verify at: curl https://${DOMAIN}/health"
```

**Step 5: Make deploy.sh executable and create .gitignore**

```bash
chmod +x deploy.sh
```

Create `.gitignore`:
```
__pycache__/
*.pyc
.pytest_cache/
.coverage
htmlcov/
*.egg-info/
dist/
build/
.env
venv/
.venv/
```

Create `.dockerignore`:
```
__pycache__
*.pyc
.pytest_cache
tests/
.git
.gitignore
docs/
*.md
requirements-dev.txt
```

**Step 6: Commit**

```bash
git add docker/ docker-compose.yml deploy.sh .gitignore .dockerignore
git commit -m "chore: Docker, Nginx, and deployment setup"
```

---

## Task 13: RapidAPI Listing & README

**Files:**
- Create: `docs/rapidapi-listing.md`
- Create: `README.md`

**Step 1: Create docs/rapidapi-listing.md**

Write marketplace listing copy following FinCalc's pattern (`E:/CLAUDE/PROJECT - INCOME/docs/rapidapi-listing.md`). Include:
- Short description (under 100 chars): "Business days, working hours & holiday calendars for 15 countries. 22 endpoints."
- Long description: problem statement, key features, country list, use cases
- Endpoint descriptions for all 22 endpoints
- Code examples in curl, Python, JavaScript for 3 key endpoints
- Pricing justification

**Step 2: Create README.md**

Write public GitHub README including:
- Badge: RapidAPI subscribers
- What it does (1 paragraph)
- Quick start (curl example for `/business-days/between`)
- Endpoint table (all 22)
- Code examples in Python and JavaScript
- Supported countries table
- Link to RapidAPI listing

**Step 3: Commit**

```bash
git add docs/rapidapi-listing.md README.md
git commit -m "docs: RapidAPI listing copy and GitHub README"
```

---

## Task 14: Dev.to Articles

**Files:**
- Create: `docs/devto-article-1-business-days-js.md`
- Create: `docs/devto-article-2-sla-deadline-python.md`
- Create: `docs/devto-article-3-holiday-aware-global.md`

Write 3 tutorial articles following the FinCalc pattern (see `E:/CLAUDE/PROJECT - INCOME/docs/devto-article-*.md`):

1. **"Calculating Business Days in JavaScript — Skip the Calendar Math"** — Build a due-date calculator using BizCal API, JavaScript fetch, async/await
2. **"Building an SLA Deadline Tracker in Python"** — Use `/working-hours/deadline`, handle DST, build a simple CLI tool
3. **"Holiday-Aware Date Math for Global Applications"** — Use `/holidays/list` + `/business-days/between` with country/region params for multi-country payroll

Each article should be 600-900 words with working code examples.

**Commit:**
```bash
git add docs/devto-article-*.md
git commit -m "docs: 3 Dev.to tutorial articles for content marketing"
```

---

## Task 15: Final Verification

**Step 1: Run full test suite one final time**

```bash
cd "E:/CLAUDE/PROJECT - BIZCAL"
pytest tests/ -v --tb=short
```
Expected: All 50+ tests PASS, 0 failures.

**Step 2: Start dev server and manually verify key endpoints**

```bash
uvicorn api.main:app --reload
```

Test these manually:
```bash
curl "http://localhost:8000/health"
curl "http://localhost:8000/business-days/between?start=2024-03-11&end=2024-03-18&country=US"
curl "http://localhost:8000/holidays/list?country=DE&region=BY&year=2024"
curl "http://localhost:8000/calendar/date-info?date=2024-12-25&country=GB"
curl "http://localhost:8000/working-hours/deadline?start=2024-03-11T09:00:00&sla_hours=24&timezone=America/New_York&country=US"
```

**Step 3: Verify OpenAPI docs render correctly**

Open browser to: `http://localhost:8000/docs`
Verify all 22 endpoints are listed and documented.

**Step 4: Final commit**

```bash
git add -A
git commit -m "chore: final verification — all tests pass, API verified"
```

---

## Manual Launch Steps (Task 16 — Requires User)

1. Create GitHub repo `bizcal-api`, push: `git remote add origin ... && git push -u origin master`
2. Replace `YOUR_GITHUB_USERNAME` in `deploy.sh`
3. Provision Hetzner CX11 VPS
4. Purchase domain (bizcalapi.com or similar)
5. Point DNS A record to VPS IP
6. SSH into VPS: `DOMAIN=bizcalapi.com EMAIL=you@email.com bash deploy.sh`
7. Verify: `curl https://bizcalapi.com/health`
8. Create RapidAPI listing → import OpenAPI from `https://bizcalapi.com/openapi.json`
9. Set pricing tiers (Free/Basic/Pro/Ultra)
10. Post Show HN
11. Post ProductHunt (Tuesday 12:01am PST)
12. Publish 3 Dev.to articles
