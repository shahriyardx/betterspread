Quick Start
===========

The example below covers the most common operations — reading, writing, appending,
clearing, and deleting — using a single async function.

.. code-block:: python

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

.. note::

   The connection is opened **lazily** — no network call is made until the first
   async method is called. You can call ``await sheet.open()`` explicitly if you
   want to pre-warm the connection.

Styling cells and rows
-----------------------

Use the :class:`~betterspread.Style` dataclass to apply formatting:

.. code-block:: python

   from betterspread import Style

   header_style = Style(
       bg_color="#4a86e8",
       text_color="#ffffff",
       bold=True,
       horizontal_align="center",
   )

   row = await tab.get_row(1)
   await row.style(header_style)

   cell = await tab.get_cell("A1")
   await cell.style(Style(bg_color="#fff2cc", italic=True))

Appending and getting the new row back
---------------------------------------

Pass ``get_row=True`` to :meth:`~betterspread.Tab.append` to receive the
appended :class:`~betterspread.Row` immediately:

.. code-block:: python

   row = await tab.append(["Bob", "25", "Designer"], get_row=True)
   print(row[0])   # "Bob"

Working with formulas
---------------------

Pass ``input_format="user_entered"`` to :meth:`~betterspread.Cell.update` so
Google Sheets evaluates the formula:

.. code-block:: python

   cell = await tab.get_cell("C1")
   cell = await cell.update("=SUM(A1:A10)", input_format="user_entered")

   # Read the formula back instead of its evaluated value
   formula_cell = await tab.get_cell("C1", render_option="formula")
   print(formula_cell)   # "=SUM(A1:A10)"
