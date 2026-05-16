from __future__ import annotations

from datetime import datetime, timezone
import heapq
from typing import Iterable

import httpx

from notification_app_be.config import settings
from notification_app_be.models import RankedNotification, SourceNotification


TYPE_WEIGHTS = {
    "placement": 100,
    "result": 70,
    "event": 40
}

UNREAD_BONUS = 30
MAX_RECENCY_SCORE = 50.0
RECENCY_DECAY_PER_HOUR = 1.0


def build_auth_header(authorization: str | None) -> dict[str, str]:
    token = authorization

    if not token and settings.AUTH_TOKEN:
        token = f"Bearer {settings.AUTH_TOKEN}"

    if not token:
        raise ValueError(
            "Authorization token missing. Pass an Authorization header or set AUTH_TOKEN in .env."
        )

    return {"Authorization": token}


async def fetch_notifications(authorization: str | None) -> list[SourceNotification]:
    headers = build_auth_header(authorization)
    url = f"{settings.BASE_URL}/notifications"

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        payload = response.json()

    raw_notifications = payload.get("notifications", [])
    return [SourceNotification.model_validate(item) for item in raw_notifications]


def compute_priority_score(
    notification: SourceNotification,
    is_read: bool,
    now: datetime
) -> tuple[float, int, int, float]:
    type_weight = TYPE_WEIGHTS.get(notification.type.lower(), 10)
    unread_bonus = 0 if is_read else UNREAD_BONUS

    age_hours = max(
        0.0,
        (now - notification.timestamp.astimezone(timezone.utc)).total_seconds() / 3600
    )
    recency_score = max(0.0, MAX_RECENCY_SCORE - (age_hours * RECENCY_DECAY_PER_HOUR))
    total_score = type_weight + unread_bonus + recency_score

    return total_score, type_weight, unread_bonus, recency_score


def rank_notifications(
    notifications: Iterable[SourceNotification],
    top_n: int,
    read_ids: set[str] | None = None
) -> list[RankedNotification]:
    read_ids = read_ids or set()
    now = datetime.now(timezone.utc)
    heap: list[tuple[float, datetime, SourceNotification, bool, int, int, float]] = []

    for notification in notifications:
        is_read = notification.id in read_ids
        score, type_weight, unread_bonus, recency_score = compute_priority_score(
            notification,
            is_read,
            now
        )
        heap_item = (
            score,
            notification.timestamp,
            notification,
            is_read,
            type_weight,
            unread_bonus,
            recency_score
        )

        if len(heap) < top_n:
            heapq.heappush(heap, heap_item)
            continue

        if heap_item[0] > heap[0][0] or (
            heap_item[0] == heap[0][0] and heap_item[1] > heap[0][1]
        ):
            heapq.heapreplace(heap, heap_item)

    ranked = sorted(heap, key=lambda item: (item[0], item[1]), reverse=True)

    return [
        RankedNotification(
            id=item[2].id,
            type=item[2].type,
            message=item[2].message,
            timestamp=item[2].timestamp,
            is_read=item[3],
            priority_score=round(item[0], 2),
            priority_rank=index + 1,
            type_weight=item[4],
            unread_bonus=item[5],
            recency_score=round(item[6], 2)
        )
        for index, item in enumerate(ranked)
    ]

