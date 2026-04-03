Cell
====

.. py:class:: Cell

   A ``str`` subclass — the cell's current value **is** the string itself.

   Obtain a ``Cell`` from :meth:`~betterspread.Tab.get_cell` or by indexing a
   :class:`~betterspread.Row`.

   .. code-block:: python

      cell = await tab.get_cell("B2")
      # or
      cell = row[1]

      print(cell)             # "hello"   (Cell is a str)
      print(cell.label)       # "B"
      print(cell.row_index)   # 2
      print(cell.cell_index)  # 1  (0-based)
      print(repr(cell))       # <Cell B2='hello'>

Attributes
----------

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Attribute
     - Type
     - Description
   * - ``label``
     - ``str``
     - Column label, e.g. ``"A"`` or ``"AA"``.
   * - ``row_index``
     - ``int``
     - 1-based row number.
   * - ``cell_index``
     - ``int``
     - 0-based column index within its parent row.
   * - ``tab``
     - ``Tab``
     - The :class:`~betterspread.Tab` this cell belongs to.
   * - ``row``
     - ``Row | None``
     - Parent :class:`~betterspread.Row`, or ``None`` when fetched via ``get_cell()``.

Methods
-------

.. py:method:: Cell.update(value, input_format="raw", render_format="formatted") -> Cell
   :async:

   Writes a new value and returns an updated ``Cell`` instance.

   :param value: The new value to write.
   :param input_format: ``"raw"`` (default) or ``"user_entered"`` (evaluates formulas).
   :type input_format: str
   :param render_format: ``"formatted"`` (default), ``"unformatted"``, or ``"formula"``.
   :type render_format: str
   :returns: A new ``Cell`` with the updated value.
   :rtype: Cell

   .. warning::

      ``Cell`` is immutable (it is a ``str``). ``update()`` returns a **new** ``Cell`` —
      reassign the variable to keep the updated value.

   .. code-block:: python

      cell = await cell.update("new value")
      cell = await cell.update("=SUM(A1:A10)", input_format="user_entered")

.. py:method:: Cell.clear()
   :async:

   Clears the cell's value.

   .. code-block:: python

      await cell.clear()

.. py:method:: Cell.style(obj)
   :async:

   Applies formatting to this cell.

   :param obj: A :class:`~betterspread.Style` instance or a raw ``gspread_formatting.CellFormat``.

   .. code-block:: python

      await cell.style(Style(bold=True, text_color="#cc0000"))

.. py:method:: Cell.delete(shift="left")
   :async:

   Deletes the cell and shifts neighbouring cells.

   :param shift: ``"left"`` (default) shifts columns left; ``"up"`` shifts rows up.
   :type shift: str

   .. code-block:: python

      await cell.delete()              # shift left (default)
      await cell.delete(shift="up")    # shift up
