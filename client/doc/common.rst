Common package
=================================================

A package of common utilities that use in different modules of the project.

Script decos.py
---------------

.. automodule:: common.decos.Logging
	:members:

Script descriptors.py
---------------------

.. autoclass:: common.descriptors.CheckPort
    :members:

.. autoclass:: common.descriptors.CheckIP
    :members:

.. autoclass:: common.descriptors.CheckName
    :members:

Script errors.py
---------------------

.. autoclass:: common.errors.ServerError
   :members:

.. autoclass:: common.errors.IncorrectDataNotDictError
   :members:

.. autoclass:: common.errors.IncorrectCodeError
   :members:

Script metaclasses.py
-----------------------

.. autoclass:: common.metaclasses.ServerCreator
   :members:

.. autoclass:: common.metaclasses.ClientCreator
   :members:

Script utils.py
---------------------

common.utils. **get_msg** (client)

	The function of receiving messages from remote computers. Accepts JSON messages, decode the received message and verifies that the dictionary is received.


common.utils. **send_msg** (sock, message)

	The function of sending dictionaries via a socket.
	Encodes a dictionary in JSON format and sends through a socket.

Script variables.py
---------------------

Contains various global project variables.