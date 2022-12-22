import asyncio
from functools import wraps
from typing import Any


def serializable(func: Any) -> Any:
    @wraps(func)
    def wrapper(*args: Any, asynchronous: bool = False, **kwargs: Any) -> Any:
        if asynchronous:
            return func(*args, **kwargs)
        else:
            # run in the current thread
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(func(*args, **kwargs))

    return wrapper
