Installation
============

Requirements
------------

* Python **≥ 3.10**
* A Google Cloud **service account** with the Sheets and Drive APIs enabled

Installing the package
----------------------

Using pip:

.. code-block:: bash

   pip install betterspread

Using `uv <https://github.com/astral-sh/uv>`_:

.. code-block:: bash

   uv add betterspread

Google API setup
----------------

1. Go to the `Google Cloud Console <https://console.cloud.google.com>`_ and create or select a project.
   Enable the **Google Sheets API** and **Google Drive API**.

2. Navigate to **APIs & Services → Credentials → Create Credentials → Service Account**.

3. Open the service account, go to the **Keys** tab, and download a **JSON** key — save it as ``credentials.json``.

4. Open your Google Sheet, click **Share**, and give the service account's ``client_email`` **Editor** access.

.. warning::

   ``credentials.json`` is listed in ``.gitignore`` by default — never commit it to version control.

Loading credentials from an environment variable
-------------------------------------------------

Instead of a file path you can pass credentials as a dict, which is useful for cloud deployments:

.. code-block:: python

   import json
   import os
   from betterspread import Connection

   con = Connection(credentials_dict=json.loads(os.environ["GOOGLE_CREDENTIALS"]))
