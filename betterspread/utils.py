import asyncio
import re
import string
from functools import partial

from gspread.utils import ValueInputOption, ValueRenderOption

# ---------------------------------------------------------------------------
# Shared format lookup tables (single source of truth for all modules)
# ---------------------------------------------------------------------------

input_formats: dict[str, ValueInputOption] = {
    "raw": ValueInputOption.raw,
    "user_entered": ValueInputOption.user_entered,
}

render_formats: dict[str, ValueRenderOption] = {
    "formatted": ValueRenderOption.formatted,
    "unformatted": ValueRenderOption.unformatted,
    "formula": ValueRenderOption.formula,
}

# ---------------------------------------------------------------------------
# Column / cell helpers
# ---------------------------------------------------------------------------

_CELL_RE = re.compile(r"^([A-Za-z]+)(\d+)$")


def char_at(length: int) -> str:
    """Return the uppercase ASCII letter at the given 1-based position (1 → 'A')."""
    return string.ascii_uppercase[length - 1]


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


# ---------------------------------------------------------------------------
# Async executor helper
# ---------------------------------------------------------------------------


async def run_in_executor(func, *args, **kwargs):
    """Run a synchronous *func* in the default thread-pool executor.

    Uses :func:`asyncio.get_running_loop` (the non-deprecated API available
    since Python 3.10) rather than the deprecated ``get_event_loop``.
    """
    bound = partial(func, *args, **kwargs)
    return await asyncio.get_running_loop().run_in_executor(None, bound)
