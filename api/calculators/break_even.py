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
