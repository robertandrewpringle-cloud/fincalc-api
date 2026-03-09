from fastapi import HTTPException

def calculate_roi(initial_investment: float, final_value: float, years: float = 1.0) -> dict:
    if initial_investment <= 0:
        raise HTTPException(status_code=422, detail="initial_investment must be greater than zero.")
    if years <= 0:
        raise HTTPException(status_code=422, detail="years must be greater than zero.")
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
