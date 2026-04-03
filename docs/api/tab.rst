Tab
===

.. py:class:: Tab

   Extends gspread's ``Worksheet`` with async helpers.

   Obtain a ``Tab`` via :meth:`~betterspread.Sheet.get_tab` or
   :meth:`~betterspread.Sheet.tabs`.

Reading
-------

.. py:method:: Tab.values(**kwargs) -> list[Row]
   :async:

   Returns every row in the sheet as a list of :class:`~betterspread.Row` objects.

   .. code-block:: python

      rows = await tab.values()
      for row in rows:
          print(row)

.. py:method:: Tab.get_row(serial_no) -> Row
   :async:

   Returns the row at the given **1-based** index.

   :param serial_no: 1-based row index.
   :type serial_no: int
   :returns: The requested row.
   :rtype: Row

   .. code-block:: python

      first_row = await tab.get_row(1)

.. py:method:: Tab.get_cell(cell_name, render_option="formatted") -> Cell
   :async:

   Fetches a single cell by its A1 address.
   Both single-letter (``B3``) and multi-letter (``AA10``) column labels are supported.

   :param cell_name: A1-notation address, e.g. ``"B3"`` or ``"AA10"``.
   :type cell_name: str
   :param render_option: ``"formatted"`` (default), ``"unformatted"``, or ``"formula"``.
   :type render_option: str
   :returns: The requested cell.
   :rtype: Cell

   .. code-block:: python

      cell    = await tab.get_cell("B2")
      formula = await tab.get_cell("C1", render_option="formula")

Writing
-------

.. py:method:: Tab.append(data, get_row=False) -> Row | None
   :async:

   Appends a new row at the bottom of the sheet.

   :param data: A flat list of values to write.
   :type data: list
   :param get_row: When ``True``, returns the appended :class:`~betterspread.Row`.
   :type get_row: bool
   :returns: The appended row when ``get_row=True``, otherwise ``None``.
   :rtype: Row | None

   .. code-block:: python

      await tab.append(["Alice", "30", "Engineer"])

      # Get the appended row back
      row = await tab.append(["Bob", "25"], get_row=True)

.. py:method:: Tab.del_row(start, end=None)
   :async:

   Deletes one or more rows by their **1-based** indices.

   :param start: 1-based index of the first row to delete.
   :type start: int
   :param end: 1-based index of the last row to delete (inclusive). Defaults to ``start``.
   :type end: int | None

   .. code-block:: python

      await tab.del_row(3)           # delete row 3
      await tab.del_row(3, end=5)    # delete rows 3, 4, and 5

.. py:method:: Tab.del_cell(start, end=None, shift="up")
   :async:

   Deletes a cell or a rectangular range, shifting the remaining cells.

   :param start: Top-left cell address, e.g. ``"B2"``.
   :type start: str
   :param end: Bottom-right cell address for a range. Defaults to ``start``.
   :type end: str | None
   :param shift: ``"up"`` (default) shifts rows up; ``"left"`` shifts columns left.
   :type shift: str

   .. code-block:: python

      await tab.del_cell("B2")                # single cell, shift up
      await tab.del_cell("B2", shift="left")  # single cell, shift left
      await tab.del_cell("A1", "C3")          # delete a 3×3 range
