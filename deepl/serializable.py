import asyncio
from functools import wraps

def serializable(func):
    @wraps(func)
    def wrapper(*args, asynchronous=False, **kwargs):
        if asynchronous:
            return func(*args, **kwargs)
        else:
            # run in the current thread
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(func(*args, **kwargs))
    return wrapper