def calculate_npv(rate: float, cash_flows: list[float]) -> dict:
    r = rate / 100
    npv = sum(cf / (1 + r) ** t for t, cf in enumerate(cash_flows))
    return {
        "npv": round(npv, 2),
        "is_profitable": npv > 0,
        "rate": rate,
        "cash_flows": cash_flows,
        "num_periods": len(cash_flows) - 1,
    }
