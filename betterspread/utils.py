import asyncio
from functools import partial


def next_char(start: str, count: int) -> str:
    next_code = ord(start) + count
    if next_code <= ord("Z"):
        return chr(next_code)
    else:
        return chr(next_code - 26)


def get_col_index(col_name: str):
    print(ord(col_name))


def to_range(start: str = "A", count: int = 0, index: int = 1):
    return f"{start}{index}:{next_char(start, count)}{index}"


async def run_in_executor(func, *args, **kwargs):
    func = partial(func, *args, **kwargs)
    data = await asyncio.get_event_loop().run_in_executor(None, func)
    return data
