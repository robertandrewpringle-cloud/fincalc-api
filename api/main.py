from fastapi import FastAPI

app = FastAPI(
    title="FinCalc API",
    description="Financial calculation endpoints for developers. Skip the math.",
    version="1.0.0",
)

@app.get("/health")
def health():
    return {"status": "ok"}
