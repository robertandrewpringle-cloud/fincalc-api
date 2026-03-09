def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 12,
) -> dict:
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
