from logging_middleware.validators import validate_log_input

from logging_middleware.client import send_log


async def Log(
    stack: str,
    level: str,
    package: str,
    message: str
):

    validate_log_input(
        stack,
        level,
        package
    )

    payload = {
        "stack": stack,
        "level": level,
        "package": package,
        "message": message
    }

    return await send_log(payload)