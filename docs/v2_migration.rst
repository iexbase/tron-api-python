Migrating your code from v1 to v2
=======================================

Changes to base API convenience methods
---------------------------------------

Tron.toDecimal()
~~~~~~~~~~~~~~~~~

In v4 ``Tron.toDecimal()`` is renamed: :meth:`~Tron.toInt` for improved clarity. It does not return a :class:`decimal.Decimal`, it returns an :class:`int`.


Removed Methods
~~~~~~~~~~~~~~~~~~

- ``Tron.toUtf8`` was removed for :meth:`~Tron.toText`.
- ``Tron.fromUtf8`` was removed for :meth:`~Tron.toHex`.
- ``Tron.toAscii`` was removed for :meth:`~Tron.toBytes`.
- ``Tron.fromAscii`` was removed for :meth:`~Tron.toHex`.
- ``Tron.fromDecimal`` was removed for :meth:`~Tron.toHex`.

Provider Access
~~~~~~~~~~~~~~~~~

In v2, ``tron.currentProvider`` was removed, in favor of ``tron.providers``.

Disambiguating String Inputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are a number of places where an arbitrary string input might be either
a byte-string that has been hex-encoded, or unicode characters in text.
These are named ``hexstr`` and ``text`` in TronAPI.
You specify which kind of :class:`str` you have by using the appropriate
keyword argument. See examples in :ref:`overview_type_conversions`.

In v1, some methods accepted a :class:`str` as the first positional argument.
In v2, you must pass strings as one of ``hexstr`` or ``text`` keyword arguments.

Notable methods that no longer accept ambiguous strings:

- :meth:`~Tron.sha3`
- :meth:`~Tron.toBytes`