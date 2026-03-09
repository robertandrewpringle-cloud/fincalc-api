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
