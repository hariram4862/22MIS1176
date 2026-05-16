from logging_middleware.constants import (
    VALID_STACKS,
    VALID_LEVELS,
    VALID_BACKEND_PACKAGES
)

from logging_middleware.exceptions import InvalidLogInputException


def validate_log_input(stack, level, package):

    if stack not in VALID_STACKS:
        raise InvalidLogInputException(
            f"Invalid stack: {stack}"
        )

    if level not in VALID_LEVELS:
        raise InvalidLogInputException(
            f"Invalid level: {level}"
        )

    if stack == "backend":
        if package not in VALID_BACKEND_PACKAGES:
            raise InvalidLogInputException(
                f"Invalid backend package: {package}"
            )