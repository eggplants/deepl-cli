import asyncio
from typing import Any

from deepl import DeepLCLI


def print_translated_text(future: asyncio.Future[str]) -> None:
    """receive the result of async func and print."""
    try:
        translated_text = future.result()
        print(translated_text)
    except asyncio.exceptions.CancelledError:
        # catch if task has been canceled via task.cancel()
        pass
    except Exception as e:  # noqa: BLE001
        print(f"Failed to translate: {e}")


async def translate(text: str) -> str:
    """translate asynchronously."""
    t = DeepLCLI("en", "ja")
    return await t.translate_async(text)


async def do_something() -> None:
    """do something asynchronously."""
    await asyncio.sleep(10)
    print("Another task done!")


if __name__ == "__main__":
    # create event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # create task to translate text and set callback
    text = "hello"
    translation_task = loop.create_task(translate(text))
    translation_task.add_done_callback(print_translated_text)

    # create another task
    another_task = loop.create_task(do_something())

    # assign tasks to event loop
    tasks: list[asyncio.Task[Any]] = [
        translation_task,
        another_task,
    ]

    wait_tasks = asyncio.wait(tasks)

    # run event loop
    loop.run_until_complete(wait_tasks)
    loop.close()
