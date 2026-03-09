from fastapi import HTTPException

def _npv_at_rate(cash_flows: list[float], rate: float) -> float:
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))

def calculate_irr(cash_flows: list[float]) -> dict:
    if cash_flows[0] >= 0:
        raise HTTPException(status_code=422, detail="First cash flow must be negative (initial investment).")
    rate = 0.1
    for _ in range(1000):
        npv = _npv_at_rate(cash_flows, rate)
        dnpv = sum(-t * cf / (1 + rate) ** (t + 1) for t, cf in enumerate(cash_flows))
        if abs(dnpv) < 1e-12:
            break
        rate_new = rate - npv / dnpv
        if rate_new <= -1:
            rate_new = -0.9999
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
