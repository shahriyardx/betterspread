import asyncio
import os
import re
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from gspread.exceptions import APIError
from gspread.utils import ValueInputOption, ValueRenderOption

# Dedicated thread pool for blocking gspread I/O, isolated from asyncio's
# default executor so sheet calls neither starve nor are starved by other
# run_in_executor users in the host application. Size is overridable via the
# BETTERSPREAD_MAX_WORKERS environment variable.
_DEFAULT_MAX_WORKERS = min(32, (os.cpu_count() or 1) + 4)
_EXECUTOR = ThreadPoolExecutor(
    max_workers=int(os.getenv("BETTERSPREAD_MAX_WORKERS") or _DEFAULT_MAX_WORKERS),
    thread_name_prefix="betterspread",
)

# Transient Google API statuses worth retrying with exponential backoff.
_RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})

input_formats: dict[str, ValueInputOption] = {
    "raw": ValueInputOption.raw,
    "user_entered": ValueInputOption.user_entered,
}

render_formats: dict[str, ValueRenderOption] = {
    "formatted": ValueRenderOption.formatted,
    "unformatted": ValueRenderOption.unformatted,
    "formula": ValueRenderOption.formula,
}

_CELL_RE = re.compile(r"^([A-Za-z]+)(\d+)$")


def get_location(length: int) -> str:
    """Convert a 1-based column number to a spreadsheet column label.

    Uses an iterative ``divmod`` algorithm that correctly handles any column
    depth — single-letter (A–Z), double-letter (AA–ZZ), triple-letter
    (AAA–XFD), and beyond.

    Examples::

        get_location(1)   → 'A'
        get_location(26)  → 'Z'
        get_location(27)  → 'AA'
        get_location(52)  → 'AZ'
        get_location(702) → 'ZZ'
        get_location(703) → 'AAA'

    Raises:
        ValueError: if *length* is not a positive integer.
    """
    if length <= 0:
        raise ValueError(f"Column number must be a positive integer, got {length!r}")

    chars: list[str] = []
    n = length
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        chars.append(chr(ord("A") + remainder))
    return "".join(reversed(chars))


def parse_cell_name(cell_name: str) -> tuple[str, int]:
    """Parse a cell address into its column label and 1-based row index.

    Works correctly for both single- and multi-letter column labels.

    Examples::

        parse_cell_name("A1")   → ("A", 1)
        parse_cell_name("AA15") → ("AA", 15)
        parse_cell_name("b3")   → ("B", 3)

    Raises:
        ValueError: if *cell_name* does not match the expected pattern.
    """
    match = _CELL_RE.match(cell_name.strip())
    if not match:
        raise ValueError(f"Invalid cell name: {cell_name!r}")
    return match.group(1).upper(), int(match.group(2))


def col_label_to_index(label: str) -> int:
    """Convert a column label to a 0-based column index.

    Examples::

        col_label_to_index("A")  → 0
        col_label_to_index("Z")  → 25
        col_label_to_index("AA") → 26
        col_label_to_index("AB") → 27
    """
    result = 0
    for char in label.upper():
        result = result * 26 + (ord(char) - ord("A") + 1)
    return result - 1


async def run_in_executor(
    func,
    *args,
    _max_retries: int = 5,
    _base_delay: float = 1.0,
    **kwargs,
):
    """Run a synchronous *func* in betterspread's dedicated thread pool.

    Transient Google API errors (HTTP 429/5xx) are retried with exponential
    backoff up to *_max_retries* times; any other error propagates
    immediately.

    Uses :func:`asyncio.get_running_loop` (the non-deprecated API available
    since Python 3.10) rather than the deprecated ``get_event_loop``.

    Args:
        func: The blocking callable to run.
        _max_retries: Maximum number of retries on a transient API error.
        _base_delay: Base seconds for the ``_base_delay * 2**attempt`` backoff.
    """
    bound = partial(func, *args, **kwargs)
    loop = asyncio.get_running_loop()

    attempt = 0
    while True:
        try:
            return await loop.run_in_executor(_EXECUTOR, bound)
        except APIError as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            if status in _RETRY_STATUSES and attempt < _max_retries:
                await asyncio.sleep(_base_delay * 2**attempt)
                attempt += 1
                continue
            raise
