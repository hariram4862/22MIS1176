import asyncio

from logging_middleware.logger import Log


async def main():

    response = await Log(
        stack="backend",
        level="error",
        package="handler",
        message="received string, expected bool"
    )

    print(response)


asyncio.run(main())