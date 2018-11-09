TRON API for Python
=====
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
    
.. image:: https://codecov.io/gh/iexbase/tron-api-python/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/iexbase/tron-api-python
    

------------

**A Command-Line Interface framework**

Installation is easy via pip:

.. code-block:: bash

    pip3 install tronapi

------------

Usage
=====
Specify the API endpoints:

.. code-block:: python
    
    from tronapi.main import Tron
    
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger()

    full_node = HttpProvider('https://api.trongrid.io')
    solidity_node = HttpProvider('https://api.trongrid.io')
    event_server = HttpProvider('https://api.trongrid.io')

    tron = Tron(full_node,
            solidity_node,
            event_server)

    account = tron.create_account()
    is_valid = bool(tron.trx.is_address(account.address.hex))

    logger.debug('Generated account: ')
    logger.debug('- Private Key: ' + account.private_key())
    logger.debug('- Public Key: ' + account.public_key())
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

