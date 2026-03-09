def calculate_mortgage(home_price: float, down_payment: float, annual_rate: float, term_years: int) -> dict:
    loan_amount = home_price - down_payment
    monthly_rate = annual_rate / 100 / 12
    n = term_years * 12
    if monthly_rate == 0:
        monthly_payment = loan_amount / n
    else:
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
