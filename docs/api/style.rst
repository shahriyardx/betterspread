Style
=====

.. py:class:: Style(bg_color="#ffffff", text_color="#000000", horizontal_align="left", vertical_align="middle", bold=False, italic=False, strikethrough=False, raw=None)

   A dataclass that builds a ``gspread_formatting.CellFormat`` from simple keyword
   arguments. Pass a ``Style`` to :meth:`~betterspread.Cell.style` or
   :meth:`~betterspread.Row.style`.

   :param bg_color: Background color as a hex string. Defaults to ``"#ffffff"``.
   :type bg_color: str
   :param text_color: Text color as a hex string. Defaults to ``"#000000"``.
   :type text_color: str
   :param horizontal_align: ``"left"`` (default), ``"center"``, or ``"right"``.
   :type horizontal_align: str
   :param vertical_align: ``"top"``, ``"middle"`` (default), or ``"bottom"``.
   :type vertical_align: str
   :param bold: Bold text. Defaults to ``False``.
   :type bold: bool
   :param italic: Italic text. Defaults to ``False``.
   :type italic: bool
   :param strikethrough: Strikethrough text. Defaults to ``False``.
   :type strikethrough: bool
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
