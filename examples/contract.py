from tronapi import Tron, HttpProvider
from solc import compile_source

full_node = HttpProvider('https://api.trongrid.io')
solidity_node = HttpProvider('https://api.trongrid.io')
event_server = HttpProvider('https://api.trongrid.io')

tron = Tron(full_node=full_node,
            solidity_node=solidity_node,
            event_server=event_server)


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
tx_data = hello.deploy(
    fee_limit=10**9,
    call_value=0,
    consume_user_resource_percent=1
)

sign = tron.trx.sign(tx_data)
result = tron.trx.broadcast(sign)
