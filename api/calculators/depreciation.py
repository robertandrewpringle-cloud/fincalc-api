from fastapi import HTTPException

def calculate_depreciation(
    asset_value: float,
    salvage_value: float,
    useful_life_years: int,
    method: str = "straight_line",
) -> dict:
    if method not in ("straight_line", "declining_balance"):
        raise HTTPException(status_code=422, detail="method must be 'straight_line' or 'declining_balance'.")
    depreciable_value = asset_value - salvage_value
    schedule = []
    if method == "straight_line":
        annual_depreciation = depreciable_value / useful_life_years
        book_value = asset_value
        for year in range(1, useful_life_years + 1):
            book_value = round(book_value - annual_depreciation, 2)
            if year == useful_life_years:
                book_value = salvage_value
            schedule.append({"year": year, "depreciation": round(annual_depreciation, 2), "book_value": book_value})
        return {"method": method, "annual_depreciation": round(annual_depreciation, 2), "schedule": schedule}
    else:
        rate = 2 / useful_life_years
        book_value = asset_value
        for year in range(1, useful_life_years + 1):
            depreciation = round(book_value * rate, 2)
            if book_value - depreciation < salvage_value:
                depreciation = round(book_value - salvage_value, 2)
            book_value = round(book_value - depreciation, 2)
            schedule.append({"year": year, "depreciation": depreciation, "book_value": book_value})
        return {"method": method, "annual_depreciation": schedule[0]["depreciation"], "schedule": schedule}
