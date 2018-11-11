Overview
========

.. contents:: :local:

The common entrypoint for interacting with the Tron library is the ``Tron``
object.  The tron object provides APIs for interacting with the tron
blockchain, typically by connecting to a HTTP server.

Providers
---------

*Providers* are how tron connects to the blockchain.  The TronAPI library comes
with a the following built-in providers that should be suitable for most normal
use cases.

- ``HttpProvider`` for connecting to http and https based servers.

The ``HttpProvider`` takes the full URI where the server can be found.  For
local development this would be something like ``http://localhost:8090``.


.. code-block:: python

    >>> from tronapi import HttpProvider, Tron

    # Note that you should create only one HttpProvider per
    # process, as it recycles underlying TCP/IP network connections between
    # your process and Tron node

    >>> full_node = HttpProvider('http://localhost:8090')
    >>> solidity_node = HttpProvider('http://localhost:8090')
    >>> event_server = HttpProvider('http://localhost:8090')

    >>> tron = Tron(full_node, solidity_node, event_server)


Base API
--------

The ``Tron`` class exposes the following convenience APIs.

.. _overview_type_conversions:

Type Conversions
~~~~~~~~~~~~~~~~

.. py:method:: Tron.toHex(primitive=None, hexstr=None, text=None)

    Takes a variety of inputs and returns it in its hexadecimal representation.

    .. code-block:: python

        >>> Tron.toHex(0)
        '0x0'
        >>> Tron.toHex(1)
        '0x1'
        >>> Tron.toHex(0x0)
        '0x0'
        >>> Tron.toHex(0x000F)
        '0xf'
        >>> Tron.toHex(b'')
        '0x'
        >>> Tron.toHex(b'\x00\x0F')
        '0x000f'
        >>> Tron.toHex(False)
        '0x0'
        >>> Tron.toHex(True)
        '0x1'
        >>> Tron.toHex(hexstr='0x000F')
        '0x000f'
        >>> Tron.toHex(hexstr='000F')
        '0x000f'
        >>> Tron.toHex(text='')
        '0x'
        >>> Tron.toHex(text='cowmö')
        '0x636f776dc3b6'

.. py:method:: Tron.toText(primitive=None, hexstr=None, text=None)

    Takes a variety of inputs and returns its string equivalent.
    Text gets decoded as UTF-8.


    .. code-block:: python

        >>> Tron.toText(0x636f776dc3b6)
        'cowmö'
        >>> Tron.toText(b'cowm\xc3\xb6')
        'cowmö'
        >>> Tron.toText(hexstr='0x636f776dc3b6')
        'cowmö'
        >>> Tron.toText(hexstr='636f776dc3b6')
        'cowmö'
        >>> Tron.toText(text='cowmö')
        'cowmö'


.. py:method:: Tron.toBytes(primitive=None, hexstr=None, text=None)

    Takes a variety of inputs and returns its bytes equivalent.
    Text gets encoded as UTF-8.


    .. code-block:: python

        >>> Tron.toBytes(0)
        b'\x00'
        >>> Tron.toBytes(0x000F)
        b'\x0f'
        >>> Tron.toBytes(b'')
        b''
        >>> Tron.toBytes(b'\x00\x0F')
        b'\x00\x0f'
        >>> Tron.toBytes(False)
        b'\x00'
        >>> Tron.toBytes(True)
        b'\x01'
        >>> Tron.toBytes(hexstr='0x000F')
        b'\x00\x0f'
        >>> Tron.toBytes(hexstr='000F')
        b'\x00\x0f'
        >>> Tron.toBytes(text='')
        b''
        >>> Tron.toBytes(text='cowmö')
        b'cowm\xc3\xb6'


.. py:method:: Tron.toInt(primitive=None, hexstr=None, text=None)

    Takes a variety of inputs and returns its integer equivalent.


    .. code-block:: python

        >>> Tron.toInt(0)
        0
        >>> Tron.toInt(0x000F)
        15
        >>> Tron.toInt(b'\x00\x0F')
        15
        >>> Tron.toInt(False)
        0
        >>> Tron.toInt(True)
        1
        >>> Tron.toInt(hexstr='0x000F')
        15
        >>> Tron.toInt(hexstr='000F')
        15

.. _overview_currency_conversions:

Currency Conversions
~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Tron.toSun(value)

    Returns the value in the denomination specified by the ``currency`` argument
    converted to sun.


    .. code-block:: python

        >>> tron.toSun(1)
        1000000


.. py:method:: Tron.fromSun(value)

    Returns the value in wei converted to the given currency. The value is returned
    as a ``Decimal`` to ensure precision down to the wei.


    .. code-block:: python

        >>> tron.fromSun(1000000)
        Decimal('1')


.. _overview_addresses:

Addresses
~~~~~~~~~~~~~~~~

.. py:method:: Tron.isAddress(value)

    Returns ``True`` if the value is one of the recognized address formats.

    .. code-block:: python

        >>> tron.isAddress('TRWBqiqoFZysoAeyR1J35ibuyc8EvhUAoY')
        True


.. _overview_hashing:


Cryptographic Hashing
~~~~~~~~~~~~~~~~~~~~~

.. py:classmethod:: Tron.sha3(primitive=None, hexstr=None, text=None)

    Returns the Keccak SHA256 of the given value. Text is encoded to UTF-8 before
    computing the hash, just like Solidity. Any of the following are
    valid and equivalent:

    .. code-block:: python

        >>> Tron.sha3(0x747874)
        >>> Tron.sha3(b'\x74\x78\x74')
        >>> Tron.sha3(hexstr='0x747874')
        >>> Tron.sha3(hexstr='747874')
        >>> Tron.sha3(text='txt')
        HexBytes('0xd7278090a36507640ea6b7a0034b69b0d240766fa3f98e3722be93c613b29d2e')

