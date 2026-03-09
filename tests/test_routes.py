from httpx import AsyncClient, ASGITransport
import pytest

@pytest.fixture
def app():
    from api.main import app
    return app

async def test_amortize_endpoint(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/amortize?principal=100000&annual_rate=5.0&term_months=12")
    assert response.status_code == 200
    data = response.json()
    assert "monthly_payment" in data
    assert "schedule" in data

async def test_mortgage_endpoint(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/mortgage?home_price=300000&down_payment=60000&annual_rate=6.5&term_years=30")
    assert response.status_code == 200
    assert response.json()["monthly_payment"] > 0

async def test_missing_param_returns_422(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/amortize?principal=100000")
    assert response.status_code == 422

async def test_npv_endpoint(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/npv?rate=10.0&cash_flows=-1000,400,400,400")
    assert response.status_code == 200

async def test_irr_endpoint(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/irr?cash_flows=-1000,1100")
    assert response.status_code == 200
    assert response.json()["irr_percent"] == pytest.approx(10.0, rel=1e-3)

async def test_amortize_zero_months_returns_422(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/amortize?principal=100000&annual_rate=5.0&term_months=0")
    assert response.status_code == 422

async def test_npv_rate_negative_100_returns_422(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/npv?rate=-100.0&cash_flows=-1000,400,400")
    assert response.status_code == 422

async def test_mortgage_zero_home_price_returns_422(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/mortgage?home_price=0&down_payment=0&annual_rate=6.5&term_years=30")
    assert response.status_code == 422
