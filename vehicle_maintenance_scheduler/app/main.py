from fastapi import FastAPI

app = FastAPI(
    title="Vehicle Maintenance Scheduler",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "message": "Vehicle Maintenance Scheduler Service Running"
    }