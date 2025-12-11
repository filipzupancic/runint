# api/main.py
from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="RunInt Benchmarks")

# Include the routes we defined earlier
app.include_router(router)

@app.get("/")
def root():
    return {"message": "RunInt Benchmark API is running. POST to /run to start a task."}