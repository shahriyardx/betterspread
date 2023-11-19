def next_char(start: str, count: int) -> str:
    next_code = ord(start) + count
    if next_code <= ord("Z"):
        return chr(next_code)
    else:
        return chr(next_code - 26)


def to_range(start: str = "A", count: int = 0):
    return f"{start}1:{next_char(start, count)}{count}"
