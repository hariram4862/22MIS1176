from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse
import httpx

from notification_app_be.config import settings
from notification_app_be.service import fetch_notifications, rank_notifications


app = FastAPI(
    title="Campus Notification Priority Inbox",
    version="1.0.0",
    description="Fetches live notifications from the upstream API and returns the top ranked items."
)


@app.get("/")
async def root() -> dict:
    return {
        "success": True,
        "message": "Priority inbox service is running",
        "data": {
            "topNDefault": settings.DEFAULT_TOP_N,
            "endpoint": "/api/v1/notifications/priority"
        }
    }


@app.get("/api/v1/notifications/priority")
async def get_priority_notifications(
    top_n: int = Query(default=settings.DEFAULT_TOP_N, ge=1, le=50),
    read_ids: list[str] | None = Query(default=None),
    authorization: str | None = Header(default=None)
):
    try:
        notifications = await fetch_notifications(authorization)
        ranked = rank_notifications(
            notifications=notifications,
            top_n=top_n,
            read_ids=set(read_ids or [])
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except HTTPException:
        raise
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="Upstream notification API rejected the authorization token."
            ) from exc
        raise HTTPException(
            status_code=502,
            detail=f"Upstream notification API returned status {exc.response.status_code}."
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch notifications from upstream API: {exc}"
        ) from exc

    return JSONResponse(
        content={
            "success": True,
            "message": "Priority notifications fetched successfully",
            "data": {
                "totalFetched": len(notifications),
                "returned": len(ranked),
                "topNotifications": [
                    item.model_dump(mode="json")
                    for item in ranked
                ]
            }
        }
    )
