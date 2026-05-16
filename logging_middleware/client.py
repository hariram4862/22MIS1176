import os
import httpx

from dotenv import load_dotenv

load_dotenv()

LOG_API_URL = os.getenv("LOG_API_URL")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")


async def send_log(payload: dict):

    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    try:

        async with httpx.AsyncClient() as client:

            response = await client.post(
                LOG_API_URL,
                json=payload,
                headers=headers,
                timeout=10
            )

            return response.json()

    except Exception:

        return {
            "message": "failed to send log"
        }