#!/usr/bin/env python3

import argparse
import json
import sys

from tronapi import config
from tronapi.tron import Tron


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Инструмент командной строки для взаимодействия с TronAPI")

    parser.add_argument(
        '--node',
        type=str,
        default=config.DEFAULT_FULL_NODE,
        help='URL полной ноды (default: "http://13.125.210.234:8090")'
    )

    subparsers = parser.add_subparsers(help='Команды')

    parser_send = subparsers.add_parser('send', help='Отправляем транзакцию')
    parser_send.set_defaults(command="send")
    parser_send.add_argument('fromaddress', type=str, help='Адрес отправителя')
    parser_send.add_argument('toaddress', type=str, help='Адрес получателя')
    parser_send.add_argument('amount', type=float, help='Сумма отправки')
    parser_send.add_argument('privatekey', type=str, help='Приватный ключ')

    parser.add_argument("--gettransaction", action="store", help="Получаем информацию о транзакции по TxID")
    parser.add_argument("--getaccount", action="store", help="Информация об аккаунте")
    parser.add_argument("--getbalance", action="store", help="Получение баланса")
    parser.add_argument("--getbandwidth", action="store",
                        help="Выбирает доступную пропускную способность для определенной учетной записи")
    parser.add_argument("--getcurrentblock", action="store_true", help="Последний номер блока")
    parser.add_argument("--gettransactioncount", action="store_true", help="Получаем общий счетчик транзакций")
    parser.add_argument("--generateaddress", action="store_true", help="Генерация нового адреса")

    args = parser.parse_args()

    tron = Tron(args.node)

    if args.getaccount:
        print_json(tron.get_account(args.getaccount))

    elif args.getbalance:
        print_json(tron.get_balance(args.getbalance))

    elif args.getbandwidth:
        print_json(tron.get_band_width(args.getbandwidth))

    elif args.gettransaction:
        print_json(tron.get_transaction(args.gettransaction))

    elif args.gettransactioncount:
        print_json(tron.get_transaction_count())

    elif args.generateaddress:
        print_json(tron.generate_address())
        exit(0)

    elif args.command == "send":
        tron.private_key = args.privatekey
        tron.send_transaction(
            from_address=args.fromaddress,
            to_address=args.toaddress,
            amount=args.amount,
        )
        exit(0)

    elif args.currentblock:
        print_json(tron.get_current_block())


def print_json(tx):
    if sys.stdout.isatty():
        print(json.dumps(tx, indent=4))
    else:
        print(tx)


if __name__ == "__main__":
    main()
