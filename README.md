# betterspread

An async Python wrapper around [gspread](https://github.com/burnash/gspread) that gives every cell and row first-class async methods — read, write, clear, style, and delete without ever leaving your `async`/`await` flow.

---

## Table of Contents

- [Why betterspread?](#why-betterspread)
- [Requirements](#requirements)
- [Installation](#installation)
- [Google API Setup](#google-api-setup)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [Connection](#connection)
  - [Sheet](#sheet)
  - [Tab](#tab)
  - [Row](#row)
  - [Cell](#cell)
  - [Style](#style)
- [Development](#development)

---

## Why betterspread?

gspread is a great library, but all its methods are synchronous and operate at the spreadsheet level. betterspread wraps it to give you:

| Feature | gspread | betterspread |
|---|---|---|
| Async-native API | ✗ | ✓ |
| Cell as a first-class object | ✗ | ✓ |
| Row as a first-class object | ✗ | ✓ |
| Per-cell `update` / `clear` / `style` / `delete` | ✗ | ✓ |
| Per-row `update` / `clear` / `style` / `delete` | ✗ | ✓ |
| Lazy connection (open on first use) | ✗ | ✓ |
| Load credentials from a file or a dict | ✗ | ✓ |

---

## Requirements

- Python **≥ 3.13**
- A Google Cloud **service account** with the Sheets and Drive APIs enabled

---

## Installation

```bash
pip install betterspread
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add betterspread
```

---

## Google API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com).
2. Create or select a project, then enable the **Google Sheets API** and **Google Drive API**.
3. Navigate to **APIs & Services → Credentials → Create Credentials → Service Account**.
4. Open the service account, go to the **Keys** tab, and download a **JSON** key — save it as `credentials.json`.
5. Open your Google Sheet, click **Share**, and give the service account's `client_email` **Editor** access.

> `credentials.json` is listed in `.gitignore` by default — never commit it.

---

## Quick Start

```python
import asyncio
from betterspread import Connection, Sheet

async def main():
    con = Connection(credentials_path="./credentials.json")
    sheet = Sheet(connection=con, sheet_name="My Spreadsheet")

    tab = await sheet.get_tab("Sheet1")

    # --- read ---
    rows = await tab.values()          # list[Row]
    row  = await tab.get_row(1)        # Row (1-based)
    cell = await tab.get_cell("B2")    # Cell

    print(cell)                        # Cell is a plain str subclass
    print(row[0].label, row[0])        # "A"  "hello"

    # --- write ---
    cell = await cell.update("world")
    await row.update(["Alice", "30", "Engineer"])

    # --- append ---
    await tab.append(["Bob", "25", "Designer"])

    # --- clear ---
    await cell.clear()
    await row.clear()

    # --- delete ---
    await row.delete()
    await cell.delete()

asyncio.run(main())
```

---

## API Reference

### Connection

Authenticates with Google and holds the underlying gspread client.

```python
Connection(
    credentials_path: Path | str | None = None,
    credentials_dict: dict | None = None,
)
```

Exactly one of the two arguments must be supplied.

| Argument | Type | Description |
|---|---|---|
| `credentials_path` | `Path \| str` | Path to a service-account JSON key file. |
| `credentials_dict` | `dict` | Service-account credentials as a dictionary (useful when loading from an environment variable). |

**Raises** `ValueError` if neither argument is provided.

#### Examples

```python
# From a file
con = Connection(credentials_path="./credentials.json")

# From an environment variable
import json, os
con = Connection(credentials_dict=json.loads(os.environ["GOOGLE_CREDENTIALS"]))
```

---

### Sheet

An async wrapper around a Google Spreadsheet. The connection is opened **lazily** — no network call is made until the first async method is called.

```python
Sheet(
    sheet_name: str,
    connection: Connection,
    folder_id: str | None = None,
)
```

| Argument | Type | Description |
|---|---|---|
| `sheet_name` | `str` | The exact title of the spreadsheet as it appears in Google Drive. |
| `connection` | `Connection` | An authenticated `Connection` instance. |
| `folder_id` | `str \| None` | Optional Drive folder ID to scope the search. |

#### Methods

##### `await sheet.open()`

Opens the remote spreadsheet. Called automatically by all other methods — you only need this if you want to pre-warm the connection.

##### `await sheet.get_tab(tab_name) → Tab`

Returns the worksheet named `tab_name` as a [`Tab`](#tab).

```python
tab = await sheet.get_tab("Sheet1")
```

##### `await sheet.tabs(exclude_hidden=False) → list[Tab]`

Returns all worksheet tabs in the spreadsheet.

```python
all_tabs = await sheet.tabs()
visible_tabs = await sheet.tabs(exclude_hidden=True)
```

---

### Tab

Extends gspread's `Worksheet` with async helpers. Obtain a `Tab` via [`Sheet.get_tab()`](#await-sheetget_tabtab_name--tab) or [`Sheet.tabs()`](#await-sheettabsexclude_hiddenfalse--listtab).

#### Reading

##### `await tab.values(**kwargs) → list[Row]`

Returns every row in the sheet as a list of [`Row`](#row) objects.

```python
rows = await tab.values()
for row in rows:
    print(row)
```

##### `await tab.get_row(serial_no) → Row`

Returns the row at the given **1-based** index.

```python
first_row = await tab.get_row(1)
```

##### `await tab.get_cell(cell_name, render_option="formatted") → Cell`

Fetches a single cell by its A1 address. Both single-letter (`B3`) and multi-letter (`AA10`) column labels are supported.

| Argument | Type | Description |
|---|---|---|
| `cell_name` | `str` | A1-notation address, e.g. `"B3"` or `"AA10"`. |
| `render_option` | `str` | `"formatted"` (default), `"unformatted"`, or `"formula"`. |

```python
cell = await tab.get_cell("B2")
formula = await tab.get_cell("C1", render_option="formula")
```

#### Writing

##### `await tab.append(data, get_row=False) → Row | None`

Appends a new row at the bottom of the sheet.

| Argument | Type | Description |
|---|---|---|
| `data` | `list` | A flat list of values to write. |
| `get_row` | `bool` | When `True`, returns the appended `Row`. |

```python
await tab.append(["Alice", "30", "Engineer"])

# Get the appended row back
row = await tab.append(["Bob", "25"], get_row=True)
```

##### `await tab.del_row(start, end=None)`

Deletes one or more rows by their **1-based** indices.

```python
await tab.del_row(3)        # delete row 3
await tab.del_row(3, end=5) # delete rows 3, 4, and 5
```

##### `await tab.del_cell(start, end=None, shift="up")`

Deletes a cell or a rectangular range, shifting the remaining cells.

| Argument | Type | Description |
|---|---|---|
| `start` | `str` | Top-left cell address, e.g. `"B2"`. |
| `end` | `str \| None` | Bottom-right cell address for a range. Defaults to `start`. |
| `shift` | `str` | `"up"` (default) shifts rows up; `"left"` shifts columns left. |

```python
await tab.del_cell("B2")               # single cell, shift up
await tab.del_cell("B2", shift="left") # single cell, shift left
await tab.del_cell("A1", "C3")         # delete a 3×3 range
```

---

### Row

A `list` subclass where every item is a [`Cell`](#cell). Obtain a `Row` from [`Tab.get_row()`](#await-tabget_rowserial_no--row), [`Tab.values()`](#await-tabvalues--listrow), or [`Tab.append(get_row=True)`](#await-tabappenddata-get_rowfalse--row--none).

Every cell in a row carries:
- its **column label** (`"A"`, `"B"`, `"AA"`, …)
- its **1-based row index**
- a **back-reference** to its parent `Row`

```python
row = await tab.get_row(1)

print(row[0])          # cell value as a string
print(row[0].label)    # "A"
print(row[0].row_index) # 1
```

#### Methods

##### `await row.update(values, start="A")`

Overwrites the row's values starting from column `start`.

```python
await row.update(["Alice", "30", "Engineer"])
await row.update(["30"], start="B")  # only update column B onward
```

##### `await row.clear()`

Clears all values in the row.

```python
await row.clear()
```

##### `await row.style(obj)`

Applies formatting to every cell in the row.  
`obj` can be a [`Style`](#style) instance or a raw `gspread_formatting.CellFormat`.

```python
from betterspread import Style
await row.style(Style(bold=True, bg_color="#ffe599"))
```

##### `await row.append_cell(value)`

Appends one or more values to the end of the row.

```python
await row.append_cell("new value")
await row.append_cell(["col1", "col2"])
```

##### `await row.refetch()`

Reloads the row's values from the remote spreadsheet.

```python
await row.refetch()
```

##### `await row.delete()`

Deletes the entire row from the sheet.

```python
await row.delete()
```

---

### Cell

A `str` subclass — the cell's current value is the string itself. Obtain a `Cell` from [`Tab.get_cell()`](#await-tabget_cellcell_name-render_optionformatted--cell) or by indexing a `Row`.

```python
cell = await tab.get_cell("B2")
# or
cell = row[1]

print(cell)            # "hello"   (Cell is a str)
print(cell.label)      # "B"
print(cell.row_index)  # 2
print(cell.cell_index) # 1  (0-based)
print(repr(cell))      # <Cell B2='hello'>
```

#### Attributes

| Attribute | Type | Description |
|---|---|---|
| `label` | `str` | Column label, e.g. `"A"` or `"AA"`. |
| `row_index` | `int` | 1-based row number. |
| `cell_index` | `int` | 0-based column index within its parent row. |
| `tab` | `Tab` | The `Tab` this cell belongs to. |
| `row` | `Row \| None` | Parent `Row`, or `None` when fetched via `get_cell()`. |

#### Methods

##### `await cell.update(value, input_format="raw", render_format="formatted") → Cell`

Writes a new value and returns an updated `Cell` instance.

| Argument | Type | Description |
|---|---|---|
| `value` | `Any` | The new value to write. |
| `input_format` | `str` | `"raw"` (default) or `"user_entered"`. |
| `render_format` | `str` | `"formatted"` (default), `"unformatted"`, or `"formula"`. |

```python
cell = await cell.update("new value")
cell = await cell.update("=SUM(A1:A10)", input_format="user_entered")
```

> `Cell` is immutable (it is a `str`). `update()` returns a **new** `Cell` — reassign the variable to keep the updated value.

##### `await cell.clear()`

Clears the cell's value.

```python
await cell.clear()
```

##### `await cell.style(obj)`

Applies formatting to this cell.  
`obj` can be a [`Style`](#style) instance or a raw `gspread_formatting.CellFormat`.

```python
await cell.style(Style(bold=True, text_color="#cc0000"))
```

##### `await cell.delete(shift="left")`

Deletes the cell and shifts neighbouring cells.

```python
await cell.delete()               # shift left (default)
await cell.delete(shift="up")     # shift up
```

---

### Style

A dataclass that builds a `gspread_formatting.CellFormat` from simple keyword arguments. Pass a `Style` to [`Cell.style()`](#await-cellistyleobj) or [`Row.style()`](#await-rowistyleobj).

```python
Style(
    bg_color: str = "#ffffff",
    text_color: str = "#000000",
    horizontal_align: str = "left",   # "left" | "center" | "right"
    vertical_align: str = "middle",   # "top"  | "middle" | "bottom"
    bold: bool = False,
    italic: bool = False,
    strikethrough: bool = False,
    raw: CellFormat | None = None,
)
```

When `raw` is provided all other arguments are ignored and the `CellFormat` is passed through unchanged.

#### Examples

```python
from betterspread import Style

# Highlight a header row
header_style = Style(
    bg_color="#4a86e8",
    text_color="#ffffff",
    bold=True,
    horizontal_align="center",
)
await row.style(header_style)

# Mark a cell as a warning
await cell.style(Style(bg_color="#fff2cc", italic=True))

# Use a pre-built CellFormat directly
from gspread_formatting import CellFormat, Color
await cell.style(Style(raw=CellFormat(backgroundColor=Color(1, 0.8, 0))))
```

---

## Development

### Setup

```bash
git clone https://github.com/shahriyar-alam/betterspread.git
cd betterspread
uv sync --group dev
```

### Running Tests

```bash
uv run pytest
```

Tests cover only the functionality betterspread adds on top of gspread — no real network calls are made.

### Project Structure

```
betterspread/
├── __init__.py       # public exports
├── connection.py     # Connection — gspread auth wrapper
├── sheet.py          # Sheet — async Spreadsheet wrapper
├── tab.py            # Tab — async Worksheet wrapper
├── row.py            # Row — list subclass
├── cell.py           # Cell — str subclass
├── style.py          # Style — CellFormat builder
└── utils.py          # shared helpers (run_in_executor, column utilities)
tests/
├── test_cell.py
├── test_connection.py
├── test_row.py
├── test_style.py
└── test_utils.py
```
