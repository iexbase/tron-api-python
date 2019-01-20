# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

import copy

from eth_abi import decode_abi
from eth_utils import (
    function_abi_to_4byte_selector,
    to_hex
)
from hexbytes import HexBytes
from trx_utils import (
    encode_hex,
    is_text,
    deprecated_for,
    combomethod
)

from tronapi.common.abi import (
    filter_by_type,
    merge_args_and_kwargs,
    abi_to_signature,
    fallback_func_abi_exists,
    check_if_arguments_can_be_encoded,
    map_abi_data
)

from tronapi.common.contracts import (
    find_matching_fn_abi,
    encode_abi,
    get_function_info,
    FallbackFn
)
from tronapi.common.datatypes import PropertyCheckingFactory
from tronapi.common.encoding import to_4byte_hex
from tronapi.common.normalizers import (
    normalize_abi,
    normalize_bytecode,
    BASE_RETURN_NORMALIZERS
)
from tronapi.exceptions import (
    NoABIFunctionsFound,
    MismatchedABI,
    FallbackNotFound
)


class NonExistentFallbackFunction:
    @staticmethod
    def _raise_exception():
        raise FallbackNotFound("No fallback function was found in the contract ABI.")

    def __getattr__(self, attr):
        return NonExistentFallbackFunction._raise_exception


class ContractFunction:
    """Base class for contract functions"""
    address = None
    function_identifier = None
    tron = None
    contract_abi = None
    abi = None
    transaction = None
    arguments = None

    def __init__(self, abi=None):
        self.abi = abi
        self.fn_name = type(self).__name__

    def __call__(self, *args, **kwargs):
        clone = copy.copy(self)
        if args is None:
            clone.args = tuple()
        else:
            clone.args = args

        if kwargs is None:
            clone.kwargs = {}
        else:
            clone.kwargs = kwargs
        clone._set_function_info()
        return clone

    def _set_function_info(self):
        if not self.abi:
            self.abi = find_matching_fn_abi(
                self.contract_abi,
                self.function_identifier,
                self.args,
                self.kwargs
            )
        if self.function_identifier is FallbackFn:
            self.selector = encode_hex(b'')
        elif is_text(self.function_identifier):
            self.selector = encode_hex(function_abi_to_4byte_selector(self.abi))
        else:
            raise TypeError("Unsupported function identifier")

        self.arguments = merge_args_and_kwargs(self.abi, self.args, self.kwargs)

    @classmethod
    def factory(cls, class_name, **kwargs):
        return PropertyCheckingFactory(class_name, (cls,), kwargs)(kwargs.get('abi'))

    def __repr__(self):
        if self.abi:
            _repr = '<Function %s' % abi_to_signature(self.abi)
            if self.arguments is not None:
                _repr += ' bound to %r' % (self.arguments,)
            return _repr + '>'
        return '<Function %s>' % self.fn_name


class ContractFunctions:
    """Class containing contract function objects
    """

    def __init__(self, abi, tron, address=None):
        if abi:
            self.abi = abi
            self._functions = filter_by_type('function', self.abi)
            for func in self._functions:
                setattr(
                    self,
                    func['name'],
                    ContractFunction.factory(
                        func['name'],
                        tron=tron,
                        contract_abi=self.abi,
                        address=address,
                        function_identifier=func['name']))

    def __iter__(self):
        if not hasattr(self, '_functions') or not self._functions:
            return

        for func in self._functions:
            yield func['name']

    def __getattr__(self, function_name):
        if '_functions' not in self.__dict__:
            raise NoABIFunctionsFound(
                "The abi for this contract contains no function definitions. ",
                "Are you sure you provided the correct contract abi?"
            )
        elif function_name not in self.__dict__['_functions']:
            raise MismatchedABI(
                "The function '{}' was not found in this contract's abi. ".format(function_name),
                "Are you sure you provided the correct contract abi?"
            )
        else:
            return super().__getattribute__(function_name)

    def __getitem__(self, function_name):
        return getattr(self, function_name)


class Contract:
    # set during class construction
    tron = None

    # instance level properties
    address = None

    # class properties (overridable at instance level)
    abi = None

    bytecode = None
    bytecode_runtime = None

    functions = None
    events = None

    def __init__(self, address=None):
        """Create a new smart contract proxy object.
        :param address: Contract address as 0x hex string
        """
        if self.tron is None:
            raise AttributeError(
                'The `Contract` class has not been initialized.  Please use the '
                '`tron.contract` interface to create your contract class.'
            )

        if address:
            self.address = self.tron.address.to_hex(address)

        if not self.address:
            raise TypeError("The address argument is required to instantiate a contract.")

        self.functions = ContractFunctions(self.abi, self.tron, self.address)
        self.fallback = Contract.get_fallback_function(self.abi, self.tron, self.address)

    @classmethod
    def factory(cls, tron, class_name=None, **kwargs):

        kwargs['tron'] = tron
        normalizers = {
            'abi': normalize_abi,
            'bytecode': normalize_bytecode,
            'bytecode_runtime': normalize_bytecode,
        }

        contract = PropertyCheckingFactory(
            class_name or cls.__name__,
            (cls,),
            kwargs,
            normalizers=normalizers
        )

        setattr(contract, 'functions', ContractFunctions(contract.abi, contract.tron))
        setattr(contract, 'fallback', Contract.get_fallback_function(contract.abi, contract.tron))

        return contract

    @classmethod
    @deprecated_for("contract.constructor.transact")
    def deploy(cls, **kwargs):
        """Deploy Contract

        Deploys a contract.
        Returns TransactionExtention, which contains an unsigned transaction.

        Example:
        .. code-block:: python
            >>> MyContract.deploy(
                fee_limit=10**9,
                call_value=0,
                consume_user_resource_percent=10
            )

        Args:
            **kwargs: Transaction parameters for the deployment
            transaction as a dict

        """
        return cls.tron.transaction_builder.create_smart_contract(
            **kwargs,
            abi=cls.abi,
            bytecode=to_hex(cls.bytecode)
        )

    @classmethod
    def constructor(cls):
        if cls.bytecode is None:
            raise ValueError(
                "Cannot call constructor on a contract that does not have 'bytecode' associated "
                "with it"
            )
        return ContractConstructor(cls.tron,
                                   cls.abi,
                                   cls.bytecode)

    @combomethod
    def encodeABI(cls, fn_name, args=None, kwargs=None, data=None):
        """Encodes the arguments using the Tron ABI for the contract function
        that matches the given name and arguments..
        """
        fn_abi, fn_selector, fn_arguments = get_function_info(
            fn_name, contract_abi=cls.abi, args=args, kwargs=kwargs,
        )

        if data is None:
            data = fn_selector

        return encode_abi(cls.tron, fn_abi, fn_arguments, data)

    @staticmethod
    def get_fallback_function(abi, tron, address=None):
        if abi and fallback_func_abi_exists(abi):
            return ContractFunction.factory(
                'fallback',
                tron=tron,
                contract_abi=abi,
                address=address,
                function_identifier=FallbackFn)()

        return NonExistentFallbackFunction()

    @combomethod
    def all_functions(self):
        return find_functions_by_identifier(
            self.abi, self.tron, self.address, lambda _: True
        )

    @combomethod
    def get_function_by_signature(self, signature):
        if ' ' in signature:
            raise ValueError(
                'Function signature should not contain any spaces. '
                'Found spaces in input: %s' % signature
            )

        def callable_check(fn_abi):
            return abi_to_signature(fn_abi) == signature

        fns = find_functions_by_identifier(self.abi, self.tron, self.address, callable_check)
        return get_function_by_identifier(fns, 'signature')

    @combomethod
    def find_functions_by_name(self, fn_name):
        def callable_check(fn_abi):
            return fn_abi['name'] == fn_name

        return find_functions_by_identifier(
            self.abi, self.tron, self.address, callable_check
        )

    @combomethod
    def get_function_by_name(self, fn_name):
        fns = self.find_functions_by_name(fn_name)
        return get_function_by_identifier(fns, 'name')

    @combomethod
    def get_function_by_selector(self, selector):
        def callable_check(fn_abi):
            return encode_hex(function_abi_to_4byte_selector(fn_abi)) == to_4byte_hex(selector)

        fns = find_functions_by_identifier(self.abi, self.tron, self.address, callable_check)
        return get_function_by_identifier(fns, 'selector')

    @combomethod
    def decode_function_input(self, data):
        data = HexBytes(data)
        selector, params = data[:4], data[4:]
        func = self.get_function_by_selector(selector)
        names = [x['name'] for x in func.abi['inputs']]
        types = [x['type'] for x in func.abi['inputs']]
        decoded = decode_abi(types, params)
        normalized = map_abi_data(BASE_RETURN_NORMALIZERS, types, decoded)
        return func, dict(zip(names, normalized))

    @combomethod
    def find_functions_by_args(self, *args):
        def callable_check(fn_abi):
            return check_if_arguments_can_be_encoded(fn_abi, args=args, kwargs={})

        return find_functions_by_identifier(
            self.abi, self.tron, self.address, callable_check
        )

    @combomethod
    def get_function_by_args(self, *args):
        fns = self.find_functions_by_args(*args)
        return get_function_by_identifier(fns, 'args')


class ContractConstructor:
    """
    Class for contract constructor API.
    """

    def __init__(self, tron, abi, bytecode):
        self.tron = tron
        self.abi = abi
        self.bytecode = bytecode

    @staticmethod
    def check_forbidden_keys_in_transaction(transaction, forbidden_keys=None):
        keys_found = set(transaction.keys()) & set(forbidden_keys)
        if keys_found:
            raise ValueError("Cannot set {} in transaction".format(', '.join(keys_found)))

    @combomethod
    def transact(self, **kwargs):
        """Deploy Contract

        Deploys a contract.
        Returns TransactionExtention, which contains an unsigned transaction.

        Args:
            **kwargs: Additional options to send
        """

        return self.tron.transaction_builder.create_smart_contract(
            **kwargs,
            abi=self.abi,
            bytecode=to_hex(self.bytecode)
        )


def find_functions_by_identifier(contract_abi, tron, address, callable_check):
    fns_abi = filter_by_type('function', contract_abi)
    return [
        ContractFunction.factory(
            fn_abi['name'],
            tron=tron,
            contract_abi=contract_abi,
            address=address,
            function_identifier=fn_abi['name'],
            abi=fn_abi
        )
        for fn_abi in fns_abi
        if callable_check(fn_abi)
    ]


def get_function_by_identifier(fns, identifier):
    if len(fns) > 1:
        raise ValueError(
            'Found multiple functions with matching {0}. '
            'Found: {1!r}'.format(identifier, fns)
        )
    elif len(fns) == 0:
        raise ValueError(
            'Could not find any function with matching {0}'.format(identifier)
        )
    return fns[0]
