Style
=====

.. py:class:: Style(bg_color=None, text_color=None, horizontal_align=None, vertical_align=None, bold=None, italic=None, strikethrough=None, raw=None)

   Builds a ``gspread_formatting.CellFormat`` from simple keyword arguments.
   Pass a ``Style`` to :meth:`~betterspread.Cell.style` or
   :meth:`~betterspread.Row.style`.

   Only the properties you pass are written. Anything left as ``None`` is
   omitted from the compiled ``CellFormat``, so applying a ``Style`` never
   clobbers formatting you did not set — ``Style(bold=True)`` makes a cell bold
   without touching its existing background, text color, or alignment.

   :param bg_color: Background color as a hex string, or ``None`` to leave unchanged.
   :type bg_color: str | None
   :param text_color: Text color as a hex string, or ``None`` to leave unchanged.
   :type text_color: str | None
   :param horizontal_align: ``"left"``, ``"center"``, ``"right"``, or ``None``.
   :type horizontal_align: str | None
   :param vertical_align: ``"top"``, ``"middle"``, ``"bottom"``, or ``None``.
   :type vertical_align: str | None
   :param bold: Bold text. ``None`` leaves it unchanged.
   :type bold: bool | None
   :param italic: Italic text. ``None`` leaves it unchanged.
   :type italic: bool | None
   :param strikethrough: Strikethrough text. ``None`` leaves it unchanged.
   :type strikethrough: bool | None
   :param raw: A pre-built ``gspread_formatting.CellFormat``. When provided, all other arguments are ignored.
   :type raw: CellFormat | None

Examples
--------

Header row with background color:

.. code-block:: python

   from betterspread import Style

   header_style = Style(
       bg_color="#4a86e8",
       text_color="#ffffff",
       bold=True,
       horizontal_align="center",
   )
   await row.style(header_style)

Warning cell with italic text:

.. code-block:: python

   await cell.style(Style(bg_color="#fff2cc", italic=True))

Passing a raw ``CellFormat`` directly:

.. code-block:: python

   from gspread_formatting import CellFormat, Color

   await cell.style(Style(raw=CellFormat(backgroundColor=Color(1, 0.8, 0))))
