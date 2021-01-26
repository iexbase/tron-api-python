===================
TRON API for Python
===================

A Python API for interacting with the Tron (TRX)

.. image:: https://img.shields.io/pypi/v/tronapi.svg
    :target: https://pypi.python.org/pypi/tronapi

.. image:: https://img.shields.io/pypi/pyversions/tronapi.svg
    :target: https://pypi.python.org/pypi/tronapi

.. image:: https://api.travis-ci.com/iexbase/tron-api-python.svg?branch=master
    :target: https://travis-ci.com/iexbase/tron-api-python
    
.. image:: https://img.shields.io/github/issues/iexbase/tron-api-python.svg
    :target: https://github.com/iexbase/tron-api-python/issues
    
.. image:: https://img.shields.io/github/issues-pr/iexbase/tron-api-python.svg
    :target: https://github.com/iexbase/tron-api-python/pulls

.. image:: https://api.codacy.com/project/badge/Grade/8a5ae1e1cc834869b1094ea3b0d24f78
   :alt: Codacy Badge
   :target: https://app.codacy.com/app/serderovsh/tron-api-python?utm_source=github.com&utm_medium=referral&utm_content=iexbase/tron-api-python&utm_campaign=Badge_Grade_Dashboard
    

------------

**A Command-Line Interface framework**

You can install it in a system-wide location via pip:

.. code-block:: bash

    sudo pip3 install tronapi

Or install it locally using `virtualenv <https://github.com/pypa/virtualenv>`__:

.. code-block:: bash

    virtualenv -p /usr/bin/python3 ~/tronapi
    source ~/tronapi/bin/activate
    pip3 install tronapi

------------

Usage
=====
Specify the API endpoints:


Smart Contract
--------------

.. code-block:: python

    from tronapi import Tron
    from solc import compile_source

    full_node = 'https://api.trongrid.io'
    solidity_node = 'https://api.trongrid.io'
    event_server = 'https://api.trongrid.io'

    tron = Tron(full_node=full_node,
            solidity_node=solidity_node,
            event_server=event_server)

    # or default (tron = Tron())


    # Solidity source code
    contract_source_code = '''
    pragma solidity ^0.4.25;

    contract Hello {
        string public message;

        function Hello(string initialMessage) public {
            message = initialMessage;
        }

        function setMessage(string newMessage) public {
            message = newMessage;
        }
    }

    '''

    compiled_sol = compile_source(contract_source_code)
    contract_interface = compiled_sol['<stdin>:Hello']

    hello = tron.trx.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
    )

    # Submit the transaction that deploys the contract
    tx = hello.deploy(
        fee_limit=10**9,
        call_value=0,
        consume_user_resource_percent=1
    )

..

Base Example
------------

.. code-block:: python
    
    from tronapi import Tron
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger()

    full_node = 'https://api.trongrid.io'
    solidity_node = 'https://api.trongrid.io'
    event_server = 'https://api.trongrid.io'

    tron = Tron(full_node=full_node,
            solidity_node=solidity_node,
            event_server=event_server)

    account = tron.create_account
    is_valid = bool(tron.trx.is_address(account.address.hex))

    logger.debug('Generated account: ')
    logger.debug('- Private Key: ' + account.private_key)
    logger.debug('- Public Key: ' + account.public_key)
    logger.debug('- Address: ')
    logger.debug('-- Base58: ' + account.address.base58)
    logger.debug('-- Hex: ' + account.address.hex)
    logger.debug('-- isValid: ' + str(is_valid))
    logger.debug('-----------')
    
    transaction = tron.trx.get_transaction('757a14cef293c69b1cf9b9d3d19c2e40a330c640b05c6ffa4d54609a9628758c')

    logger.debug('Transaction: ')
    logger.debug('- Hash: ' + transaction['txID'])
    logger.debug('- Transaction: ' + json.dumps(transaction, indent=2))
    logger.debug('-----------')
    
    # Events
    event_result = tron.trx.get_event_result('TGEJj8eus46QMHPgWQe1FJ2ymBXRm96fn1', 0, 'Notify')

    logger.debug('Event result:')
    logger.debug('Contract Address: TGEJj8eus46QMHPgWQe1FJ2ymBXRm96fn1')
    logger.debug('Event Name: Notify')
    logger.debug('Block Number: 32162')
    logger.debug('- Events: ' + json.dumps(event_result, indent=2))

More samples and snippets are available at `examples <https://github.com/iexbase/tron-api-python/tree/master/examples>`__.

Documentation
=============

Documentation is available at `docs <https://tronapi-for-python.readthedocs.io/en/latest/>`__.


Donations
=============

TRON: TRWBqiqoFZysoAeyR1J35ibuyc8EvhUAoY

