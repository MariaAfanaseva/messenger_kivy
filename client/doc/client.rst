Client module documentation
=================================================

Client messaging application. Supports
messages are online, messages are encrypted
using the RSA algorithm with a long key of 2048 bits.

Supports command line arguments:

``python client_main.py -ip {ip server} -port {port} -n or --name {user login} -p или -password {password}``

1. {ip server} ``-ip`` - message server address
2. {port} ``- port``  - on which connections are accepted.
3. ``-n`` or ``--name`` - username with which to log in.
4. ``-p`` or ``--password`` - user password.

Все опции командной строки являются необязательными, но имя пользователя и пароль необходимо использовать в паре.

Examples of using:

* ``python client_main.py``

*Running the application with default settings.*

* ``python client_main.py 127.0.0.1 7777``

*Launching the application with instructions to connect to the server at ip_address:port*

* ``python client_main.py -n test1 -p 123``

* Launching the application with user test1 and password 123. *

* ``python client_main.py ip_address some_port -n test1 -p 123``

* Launching the application with the user test1 and password 123 and instructing to connect to the server at ip_address: port. *

client_main.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Launched module, contains parser of command line arguments and application initialization functionality.

client. **get_args** ()

    Parser of command line arguments, returns a tuple of 4 elements:

    * server address
    * port
    * Username
    * password

.. autoclass:: client_main.Client
	:members:

.. autoclass:: client_main.ClientTransport
	:members:

database_client.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: database_client.ClientDB
	:members:

encrypt_decrypt.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: encrypt_decrypt.EncryptDecrypt
	:members:
