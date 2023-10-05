from CaaS import router as app


@app.get("/api/test")
async def index() -> dict:
    return {
        "data": "Test data"
    }