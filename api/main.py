from fastapi import FastAPI
from api.routes.calculators import router

app = FastAPI(
    title="FinCalc API",
    description="Financial calculation endpoints for developers. Skip the math. 8 endpoints covering amortization, compound interest, ROI, NPV, IRR, break-even, depreciation, and mortgage.",
    version="1.0.0",
    contact={"name": "FinCalc API", "url": "https://rapidapi.com"},
)

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}
