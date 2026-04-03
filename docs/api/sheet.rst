Sheet
=====

.. py:class:: Sheet(sheet_name, connection, folder_id=None)

   An async wrapper around a Google Spreadsheet.

   The connection is opened **lazily** — no network call is made until the first
   async method is called.

   :param sheet_name: The exact title of the spreadsheet as it appears in Google Drive.
   :type sheet_name: str
   :param connection: An authenticated :class:`~betterspread.Connection` instance.
   :type connection: Connection
   :param folder_id: Optional Drive folder ID to scope the search.
   :type folder_id: str | None

Methods
-------

.. py:method:: Sheet.open()
   :async:

   Opens the remote spreadsheet. Called automatically by all other methods — only
   call this explicitly if you want to pre-warm the connection.

   .. code-block:: python

      await sheet.open()

.. py:method:: Sheet.get_tab(tab_name) -> Tab
   :async:

   Returns the worksheet named ``tab_name`` as a :class:`~betterspread.Tab`.

   :param tab_name: The exact name of the worksheet tab.
   :type tab_name: str
   :returns: The matching worksheet.
   :rtype: Tab

   .. code-block:: python

      tab = await sheet.get_tab("Sheet1")

.. py:method:: Sheet.tabs(exclude_hidden=False) -> list[Tab]
   :async:

   Returns all worksheet tabs in the spreadsheet.

   :param exclude_hidden: When ``True``, hidden tabs are omitted.
   :type exclude_hidden: bool
   :returns: All visible (or all) tabs.
   :rtype: list[Tab]

   .. code-block:: python

      all_tabs     = await sheet.tabs()
      visible_tabs = await sheet.tabs(exclude_hidden=True)
