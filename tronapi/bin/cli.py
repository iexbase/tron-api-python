#!/usr/bin/env python3

import argparse
import json
import sys

from tronapi.constants import DEFAULT_FULL_NODE, DEFAULT_SOLIDITY_NODE, DEFAULT_EVENT_SERVER
from tronapi import Tron


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Command line tool for interacting with TronAPI")

    parser.add_argument(
        '--node',
        type=str,
        default=DEFAULT_FULL_NODE,
        help='URL полной ноды (default: "http://api.trongrid.io")'
    )

    subparsers = parser.add_subparsers(help='Commands')

    parser_send = subparsers.add_parser('send', help='Send transaction')
    parser_send.set_defaults(command="send")
    parser_send.add_argument('fromaddress', type=str, help='From address')
    parser_send.add_argument('toaddress', type=str, help='To address')
    parser_send.add_argument('amount', type=float, help='Amount')
    parser_send.add_argument('privatekey', type=str, help='Private key')

    parser.add_argument("--gettransaction", action="store", help="Get TxID transaction information")
    parser.add_argument("--getaccount", action="store", help="Account Information")
    parser.add_argument("--getbalance", action="store", help="Getting a balance")
    parser.add_argument("--getbandwidth", action="store",
                        help="Query bandwidth information.")
    parser.add_argument("--getcurrentblock", action="store_true", help="Last block number")
    parser.add_argument("--gettransactioncount", action="store_true", help="Get the total transaction count")
    parser.add_argument("--generateaddress", action="store_true", help="Generate new address")

    args = parser.parse_args()

    tron = Tron(args.node, DEFAULT_SOLIDITY_NODE, DEFAULT_EVENT_SERVER)

    if args.getaccount:
        print_json(tron.trx.get_account(args.getaccount))

    elif args.getbalance:
        print_json(tron.trx.get_balance(args.getbalance))

    elif args.getbandwidth:
        print_json(tron.trx.get_band_width(args.getbandwidth))

    elif args.gettransaction:
        print_json(tron.trx.get_transaction(args.gettransaction))

    elif args.gettransactioncount:
        print_json(tron.trx.get_transaction_count())

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
