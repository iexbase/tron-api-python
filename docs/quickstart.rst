Quickstart
==========

.. contents:: :local:

.. NOTE:: All code starting with a ``$`` is meant to run on your terminal.
    All code starting with a ``>>>`` is meant to run in a python interpreter,
    like `ipython <https://pypi.org/project/ipython/>`_.

Installation
------------

TronAPI can be installed (preferably in a :ref:`virtualenv <setup_environment>`)
using ``pip`` as follows:

.. code-block:: shell

   $ pip install tronapi


.. NOTE:: If you run into problems during installation, you might have a
    broken environment. See the troubleshooting guide to :ref:`setup_environment`.


Installation from source can be done from the root of the project with the
following command.

.. code-block:: shell

   $ pip install .


Using TronAPI
----------

To use the tron library you will need to initialize the
:class:`~tronapi` class.

.. code-block:: python

    >>> from tronapi import Tron
    >>> full_node = HttpProvider('https://api.trongrid.io')
    >>> solidity_node = HttpProvider('https://api.trongrid.io')
    >>> event_server = 'https://api.trongrid.io'
    >>>
    >>> tron = Tron(full_node, solidity_node, event_server)
    >>> tron.default_block = 'latest'


Getting Blockchain Info
----------------------------------------

It's time to start using TronAPI for Python! Try getting all the information about the latest block.

.. code-block:: python

    >>> tron.get_block('latest')
    >>> {
    "blockID": "00000000003a5bbda4aea15cb5d99230674463e9d5f2c0c647316839b25fd5b9",
    "block_header": {
        "raw_data": {
            "number": 3824573,
            "txTrieRoot": "31ee3e2ed28f843bf1d53495beece2f5b9c76480772f0106e17156fb0066c3a2",
            "witness_address": "41f70386347e689e6308e4172ed7319c49c0f66e0b",
            "parentHash": "00000000003a5bbc1e78e3144ad52f01a27b8f7acceb98d3ca09c1abea5cd32a",
            "version": 3,
            "timestamp": 1541425827000
        },
        "witness_signature": "fddc729f55c0ecc6f9cf4ab17cf818ddc0e85d2c21382ed6b1430adb1dcd13006c24ae0e08f16d29362452ec8869d29a28d57a85d6cec30ef60c2a37332fdb4d00"
    },
    "transactions": [

    ]
}



