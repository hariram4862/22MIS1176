import httpx

from vehicle_maintenance_scheduler.app.config.settings import settings


headers = {
    "Authorization": f"Bearer {settings.AUTH_TOKEN}"
}


async def get_data(endpoint: str):

    async with httpx.AsyncClient() as client:

        response = await client.get(
            f"{settings.BASE_URL}/{endpoint}",
            headers=headers
        )

        response.raise_for_status()

        return response.json()