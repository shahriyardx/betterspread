Why betterspread?
=================

`gspread <https://github.com/burnash/gspread>`_ is a great library, but all its methods are synchronous
and operate at the spreadsheet level. **betterspread** wraps it to give you:

.. list-table::
   :header-rows: 1
   :widths: 50 25 25

   * - Feature
     - gspread
     - betterspread
   * - Async-native API
     - ✗
     - ✓
   * - Cell as a first-class object
     - ✗
     - ✓
   * - Row as a first-class object
     - ✗
     - ✓
   * - Per-cell ``update`` / ``clear`` / ``style`` / ``delete``
     - ✗
     - ✓
   * - Per-row ``update`` / ``clear`` / ``style`` / ``delete``
     - ✗
     - ✓
   * - Lazy connection (open on first use)
     - ✗
     - ✓
   * - Load credentials from a file or a dict
     - ✗
     - ✓
