from fastapi import FastAPI

from vehicle_maintenance_scheduler.app.api.routes import router

app = FastAPI(
    title="Vehicle Maintenance Scheduler"
)

app.include_router(router)


@app.get("/")
async def root():

    return {
        "message": "Vehicle Maintenance Scheduler Running"
    }