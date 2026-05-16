from pydantic import BaseModel
from typing import List


class DepotSchedule(BaseModel):
    depot_id: int
    mechanic_hours: int
    total_impact: int
    total_duration: int
    selected_task_count: int
    selected_tasks: List[str]


class ScheduleResponse(BaseModel):
    schedules: List[DepotSchedule]