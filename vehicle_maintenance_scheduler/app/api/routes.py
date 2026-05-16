from fastapi import APIRouter

from vehicle_maintenance_scheduler.app.utils.api_client import get_data

from vehicle_maintenance_scheduler.app.services.scheduler_service import (
    optimize_tasks
)

from vehicle_maintenance_scheduler.app.models.schedule_models import (
    ScheduleResponse
)

router = APIRouter()


@router.get(
    "/schedule",
    response_model=ScheduleResponse
)
async def generate_schedule():

    depots_response = await get_data("depots")
    vehicles_response = await get_data("vehicles")

    depots = depots_response["depots"]
    vehicles = vehicles_response["vehicles"]

    schedules = []

    for depot in depots:

        optimized = optimize_tasks(
            vehicles,
            depot["MechanicHours"]
        )

        selected_tasks = [
            task["TaskID"]
            for task in optimized["selected_tasks"]
        ]

        schedules.append({
            "depot_id": depot["ID"],
            "mechanic_hours": depot["MechanicHours"],
            "total_impact": optimized["total_impact"],
            "total_duration": optimized["total_duration"],
            "selected_task_count": len(selected_tasks),
            "selected_tasks": selected_tasks
        })

    return {
        "schedules": schedules
    }