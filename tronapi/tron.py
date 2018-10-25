# -*- coding: utf-8 -*-

# Copyright 2018 iEXBase
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
    Tron API from Python
"""

import base58
import math

from tronapi.crypto import utils
from tronapi.provider import HttpProvider


class Tron:

    def __init__(self, full_node, solidity_node=None, private_key=None):

        if isinstance(full_node, str):
            full_node = HttpProvider(full_node)

        if isinstance(solidity_node, str):
            solidity_node = HttpProvider(solidity_node)

        self.full_node = full_node
        self.solidity_node = solidity_node

        if private_key:
            self.private_key = private_key

    @staticmethod
    def is_valid_provider(provider):
        """Проверка провайдера

        Args:
            provider(str): Провайдер

        Returns:
           True в случае успеха, False в противном случае.

        """
        return isinstance(provider, HttpProvider)

    def get_current_block(self):
        """Последний номер блока"""
        return self.full_node.request('/wallet/getnowblock')

    def get_block(self, block=None):
        """Получаем детали блока с помощью HashString или blockNumber

        Args:
            block (int | str): Номер или Хэш блока

        """
        if block is None:
            raise Exception('No block identifier provided')

        if block == 'latest':
            return self.get_current_block()

        if type(block) is str:
            return self.get_block_by_hash(block)

        return self.get_block_by_number(block)

    def get_block_by_hash(self, hash_block):
        """Получаем детали блока по хэшу

        Args:
            hash_block (str): Хэш блока

        """
        return self.full_node.request('/wallet/getblockbyid', {
            'value': hash_block
        })

    def get_block_by_number(self, block_id):
        """Получаем детали блока по номеру

        Args:
            block_id (int): Номер блока

        """
        if not utils.is_integer(block_id) or block_id < 0:
            raise Exception('Invalid block number provided')

        return self.full_node.request('/wallet/getblockbynum', {
            'num': int(block_id)
        })

    def get_block_transaction_count(self, block=None):
        """Получаем детали блока по номеру

        Args:
            block (int | str): Номер или Хэш блока

        """
        transaction = self.get_block(block)['transactions']

        if transaction == 0:
            return 0

        return len(transaction)

    def get_transaction_from_block(self, block=None, index=0):
        """Получаем детали транзакции из Блока

        Args:
            block (int | str): Номер или Хэш блока
            index (int) Позиция транзакции

        """
        if not utils.is_integer(index) or index < 0:
            raise Exception('Invalid transaction index provided')

        transactions = self.get_block(block)['transactions']

        if not transactions or len(transactions) < index:
            raise Exception('Transaction not found in block')

        return transactions[index]

    def get_transaction(self, transaction_id):
        """Получаем информацию о транзакции по TxID

        Args:
            transaction_id (str): Хэш транзакции

        """
        response = self.full_node.request('/wallet/gettransactionbyid', {
            'value': transaction_id
        }, 'post')

        if not response:
            raise Exception('Transaction not found')

        return response

    def get_account(self, address):
        """Информация об аккаунте

        Args:
            address (str): Адрес учетной записи

        """
        return self.full_node.request('/wallet/getaccount', {
            'address': self.to_hex(address)
        }, 'post')

    def get_balance(self, address, from_tron=False):
        """Получение баланса

        Args:
            address (str): Адрес учетной записи
            from_tron (bool): Преобразовать в обычный формат

        """
        response = self.get_account(address)
        if from_tron:
            return self.from_tron(response['balance'])

        return response['balance']

    def get_transactions_related(self, address, direction='to', limit=30, offset=0):
        """Получение транзакций по направлениям "from" и "to"

        Args:
            address (str): Адрес учетной записи
            direction (str): Тип направления
            limit (int): Записей на странице
            offset (int): Страница

        """

        if direction not in ['from', 'to']:
            raise Exception('Invalid direction provided: Expected "to", "from"')

        if not isinstance(limit, int) or limit < 0:
            raise Exception('Invalid limit provided')

        if not isinstance(offset, int) or offset < 0:
            raise Exception('Invalid offset provided')

        response = self.solidity_node.request('/walletextension/gettransactions{}this'.format(direction), {
            'account': {'address': self.to_hex(address)},
            'limit': limit,
            'offset': offset
        }, 'post')

        merge = dict(response)
        merge.update({'direction': direction})
        return merge

    def get_transactions_to_address(self, address, limit=30, offset=0):
        """Получение транзакций по направлении "to"

        Args:
            address (str): Адрес учетной записи
            limit (int): Записей на странице
            offset (int): Страница

        """
        return self.get_transactions_related(address, 'to', limit, offset)

    def get_transactions_from_address(self, address, limit=30, offset=0):
        """Получение транзакций по направлении "from"

        Args:
            address (str): Адрес учетной записи
            limit (int): Записей на странице
            offset (int): Страница

        """
        return self.get_transactions_related(address, 'from', limit, offset)

    def get_band_width(self, address):
        """Выбирает доступную пропускную способность для определенной учетной записи

        Args:
            address (str): Адрес учетной записи

        """
        return self.full_node.request('/wallet/getaccountnet', {
            'address': self.to_hex(address)
        })

    def get_transaction_count(self):
        """Получаем общий счетчик транзакций

        Note: Считывается все транзакции блокчейн сети Tron

        Examples:
            >>> tron.get_transaction_count()

        Returns:
            Получение результата в виде строки

        """
        response = self.full_node.request('/wallet/totaltransaction')

        return response['num']

    def send_transaction(self, from_address, to_address, amount):
        """Отправляем транзакцию в Blockchain

        Args:
            from_address (str): Адрес отправителя
            to_address (str): Адрес получателя
            amount (float): Сумма отправки

        Returns:
            Возвращает детали отправляемой транзакции
            [result=1] - Успешно отправлено

        """
        if not self.private_key:
            raise Exception('Missing private key')

        transaction = self._create_transaction(from_address, to_address, amount)
        sign = self._sign_transaction(transaction)
        response = self._send_raw_transaction(sign)

        result = dict(sign)
        result.update(response)

        return result

    def _create_transaction(self, from_address, to_address, amount):
        """Создаем неподписанную транзакцию

        Args:
            from_address (str): Адрес отправителя
            to_address (str): Адрес получателя
            amount (float): Сумма отправки

        Returns:
            Возвращает неподписанную транзакцию

        """

        if type(amount) != float or amount < 0:
            raise Exception('Invalid amount provided')

        _to = self.to_hex(to_address)
        _from = self.to_hex(from_address)

        if _to == _from:
            raise Exception('Cannot transfer TRX to the same account')

        return self.full_node.request('/wallet/createtransaction', {
            'to_address': _to,
            'owner_address': _from,
            'amount': self.to_tron(amount)
        }, 'post')

    def _sign_transaction(self, transaction):
        """Подписываем транзакцию

        Note: Транзакции подписываются только с использованием приватного ключа

        Args:
            transaction (object): Детали транзакции

        """
        if 'signature' in transaction:
            raise Exception('Transaction is already signed')

        return self.full_node.request('/wallet/gettransactionsign', {
            'transaction': transaction,
            'privateKey': self.private_key
        }, 'post')

    def _send_raw_transaction(self, signed):
        """Отправляем подписанную транзакцию

        Note: Если транзакция подписана то отправляем в сеть tron

        Args:
            signed (object): Детали подписанной транзакции

        """
        if not type({}) is dict:
            raise Exception('Invalid transaction provided')

        if 'signature' not in signed:
            raise Exception('Transaction is not signed')

        return self.full_node.request('/wallet/broadcasttransaction', signed, 'post')

    def update_account(self, address, name):
        """Изменить имя учетной записи

        Note: Имя пользователя разрешается редактировать только один раз

        Args:
            address (str): Адрес учетной записи
            name (str): Новое имя

        """
        transaction = self.full_node.request('/wallet/updateaccount', {
            'account_name': self.string_utf8_to_hex(name),
            'owner_address': self.to_hex(address)
        })

        sign = self._sign_transaction(transaction)
        response = self._send_raw_transaction(sign)

        return response

    def register_account(self, address, new_account_address):
        """Регистрация новой учетной записи в сети

        Args:
            address (str): Адрес учетной записи
            new_account_address (str): Новый адрес

        """
        return self.full_node.request('/wallet/createaccount', {
            'owner_address': self.to_hex(address),
            'account_address': self.to_hex(new_account_address)
        }, 'post')

    def apply_for_super_representative(self, address, url):
        """Выдвигать кандидатуру супер представителя

        Note: Применяется, чтобы стать супер представителем. Стоимость 9999 TRX.

        Args:
            address (str): Адрес учетной записи
            url (str): Адрес сайта

        """
        return self.full_node.request('/wallet/createwitness', {
            'owner_address': self.to_hex(address),
            'url': self.string_utf8_to_hex(url)
        }, 'post')

    def list_nodes(self):
        """Список доступных нодов"""
        return self.full_node.request('/wallet/listnodes')

    def get_tokens_issued_by_address(self, address):
        """Попытки найти токен с адресом учетной записи, который его выпустил

        Args:
            address (str): Адрес учетной записи

        """
        return self.full_node.request('/wallet/getassetissuebyaccount', {
            'address': self.to_hex(address)
        }, 'post')

    def get_token_from_id(self, token_id):
        """Попытки найти токен по имени

        Args:
            token_id (str): ID токена

        """
        return self.full_node.request('/wallet/getassetissuebyname', {
            'value': self.string_utf8_to_hex(token_id)
        })

    def get_block_range(self, start, end):
        """Получаем список блоков из определенного диапазона

        Args:
            start (int): Начало
            end (int): Конец

        """
        if not utils.is_integer(start) or start < 0:
            raise Exception('Invalid start of range provided')

        if not utils.is_integer(end) or end <= start:
            raise Exception('Invalid end of range provided')

        return self.full_node.request('/wallet/getblockbylimitnext', {
            'startNum': int(start),
            'endNum': int(end) + 1
        }, 'post')['block']

    def get_latest_blocks(self, limit=1):
        """Получаем список последних блоков

        Args:
            limit (int): Количество блоков

        """
        if not utils.is_integer(limit) or limit <= 0:
            raise Exception('Invalid limit provided')

        return self.full_node.request('/wallet/getblockbylatestnum', {
            'limit': limit
        }, 'post')['block']

    def list_super_representatives(self):
        """Получаем список суперпредставителей

        Examples:
            >>> tron.list_super_representatives()

        """
        return self.full_node.request('/wallet/listwitnesses')['witnesses']

    def list_tokens(self, limit=0, offset=0):
        """Получаем список выпущенных токенов

        Args:
            limit (int): Количество токенов на странице
            offset (int): Страницы

        """
        if not utils.is_integer(limit) or (limit and offset < 1):
            raise Exception('Invalid limit provided')

        if not utils.is_integer(offset) or offset < 0:
            raise Exception('Invalid offset provided')

        if not limit:
            return self.full_node.request('/wallet/getassetissuelist')['assetIssue']

        return self.full_node.request('/wallet/getpaginatedassetissuelist', {
            'limit': int(limit),
            'offset': int(offset)
        }, 'post')

    def time_until_next_vote_cycle(self):
        """Возвращает время в миллисекундах до следующего подсчета голосов SR"""
        num = self.full_node.request('/wallet/getnextmaintenancetime')['num']

        if num == -1:
            exit('Failed to get time until next vote cycle')

        return math.floor(num / 1000)

    def validate_address(self, address, hex=False):
        """Проверка адресов на действительность

        Args:
            address (str): Адрес учетной записи
            hex (bool): Формат адреса

        """
        if hex:
            address = self.to_hex(address)

        return self.full_node.request('/wallet/validateaddress', {
            'address': address
        }, 'post')

    def generate_address(self):
        """Генерация нового адреса"""
        return self.full_node.request('/wallet/generateaddress')

    @staticmethod
    def string_utf8_to_hex(name):
        """ Преобразование строки в формат Hex

        Args:
            name (str): Строка

        """
        return bytes(name, encoding='utf-8').hex()

    @staticmethod
    def to_tron(amount):
        """Преобразовываем сумму в формат Tron

        Args:
            amount (float): Сумма

        """
        return math.floor(amount * 1e6)

    @staticmethod
    def from_tron(amount):
        """Преобразовываем сумму из формата Tron

        Args:
            amount (int): Сумма

        """
        return abs(amount) / 1e6

    @staticmethod
    def to_hex(address):
        """Получить адресную запись hexString

        Args:
            address (str): Строки, которые необходимо зашифровать

        """
        return base58.b58decode_check(address).hex().upper()

    @staticmethod
    def from_hex(address):
        """Отменить шестнадцатеричную строку

        Args:
            address (str): шестнадцатеричная строка

        """
        return base58.b58encode_check(bytes.fromhex(address))

    def is_connected(self):
        """Проверка всех подключенных нодов"""
        full_node = False
        solidity_node = False

        if self.full_node:
            full_node = self.full_node.is_connected()

        if self.solidity_node:
            solidity_node = self.solidity_node.is_connected()

        return {
            'fullNode': full_node,
            'solidityNode': solidity_node
        }
