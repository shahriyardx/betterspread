Row
===

.. py:class:: Row

   A ``list`` subclass where every item is a :class:`~betterspread.Cell`.

   Obtain a ``Row`` from :meth:`~betterspread.Tab.get_row`,
   :meth:`~betterspread.Tab.values`, or :meth:`~betterspread.Tab.append` (with
   ``get_row=True``).

   Every cell in a row carries its **column label** (``"A"``, ``"B"``, ``"AA"``, …),
   its **1-based row index**, and a **back-reference** to its parent ``Row``.

   .. code-block:: python

      row = await tab.get_row(1)

      print(row[0])             # cell value as a string
      print(row[0].label)       # "A"
      print(row[0].row_index)   # 1

Methods
-------

.. py:method:: Row.update(values, start="A")
   :async:

   Overwrites the row's values starting from column ``start``.

   :param values: New values to write.
   :type values: list
   :param start: Column label to start writing from. Defaults to ``"A"``.
   :type start: str

   .. code-block:: python

      await row.update(["Alice", "30", "Engineer"])
      await row.update(["30"], start="B")   # update column B onward only

.. py:method:: Row.clear()
   :async:

   Clears all values in the row.

   .. code-block:: python

      await row.clear()

.. py:method:: Row.style(obj)
   :async:

   Applies formatting to every cell in the row.

   :param obj: A :class:`~betterspread.Style` instance or a raw ``gspread_formatting.CellFormat``.

   .. code-block:: python

      from betterspread import Style
      await row.style(Style(bold=True, bg_color="#ffe599"))

.. py:method:: Row.append_cell(value)
   :async:

   Appends one or more values to the end of the row.

   :param value: A single value or a list of values.

   .. code-block:: python

      await row.append_cell("new value")
      await row.append_cell(["col1", "col2"])

.. py:method:: Row.refetch()
   :async:

   Reloads the row's values from the remote spreadsheet.

   .. code-block:: python

      await row.refetch()

.. py:method:: Row.delete()
   :async:

   Deletes the entire row from the sheet.

   .. code-block:: python

      await row.delete()
