def calculate_amortization(principal: float, annual_rate: float, term_months: int) -> dict:
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
