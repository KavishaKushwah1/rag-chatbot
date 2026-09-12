"""
Bridges a synchronous generator (stream_completion) into an async
generator that runs in a background thread. Without this, consuming a
sync generator inside an async def blocks the entire event loop for the
duration of every yield — meaning one user's slow LLM call freezes every
other concurrent user's request. Confirmed via load testing: an
unrelated simple query took 19s instead of ~3s while a heavy query was
in flight, before this fix.
"""
from __future__ import annotations
import asyncio
import queue
import threading
from collections.abc import Callable, AsyncIterator


async def iterate_in_thread(sync_gen_factory: Callable, *args, **kwargs) -> AsyncIterator:
    loop = asyncio.get_event_loop()
    q: queue.Queue = queue.Queue()

    def worker():
        try:
            for item in sync_gen_factory(*args, **kwargs):
                q.put(("item", item))
        except Exception as e:
            q.put(("error", e))
        finally:
            q.put(("done", None))

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    while True:
        kind, value = await loop.run_in_executor(None, q.get)
        if kind == "item":
            yield value
        elif kind == "error":
            raise value
        else:
            break