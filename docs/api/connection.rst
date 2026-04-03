Connection
==========

.. py:class:: Connection(credentials_path=None, credentials_dict=None)

   Authenticates with Google and holds the underlying gspread client.

   Exactly one of ``credentials_path`` or ``credentials_dict`` must be supplied.

   :param credentials_path: Path to a service-account JSON key file.
   :type credentials_path: Path | str | None
   :param credentials_dict: Service-account credentials as a dictionary (useful when loading from an environment variable).
   :type credentials_dict: dict | None
   :raises ValueError: If neither argument is provided.

Examples
--------

From a file:

.. code-block:: python

   from betterspread import Connection

   con = Connection(credentials_path="./credentials.json")

From an environment variable:

.. code-block:: python

   import json
   import os
   from betterspread import Connection

   con = Connection(credentials_dict=json.loads(os.environ["GOOGLE_CREDENTIALS"]))
