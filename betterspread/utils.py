import asyncio
import math
import string
from functools import partial


def chat_at(length):
    return string.ascii_uppercase[length - 1]


def get_location(length):
    if length <= 26:
        return f"{chat_at(length)}"

    iteration = math.ceil(length / 26)
    first_char = chat_at(iteration - 1)
    second_char = chat_at(length % 26)

    return f"{first_char}{second_char}"


async def run_in_executor(func, *args, **kwargs):
    func = partial(func, *args, **kwargs)
    data = await asyncio.get_event_loop().run_in_executor(None, func)
    return data
