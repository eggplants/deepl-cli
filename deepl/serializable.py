import asyncio
from functools import wraps
from typing import Any


def serializable(func: Any) -> Any:  # noqa: ANN401
    @wraps(func)
    def wrapper(*args: Any, asynchronous: bool = False, **kwargs: Any) -> Any:  # noqa: ANN401
        if asynchronous:
            return func(*args, **kwargs)

        # run in the current thread
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return wrapper
