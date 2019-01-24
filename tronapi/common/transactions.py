from tronapi.common.threads import Timeout


def wait_for_transaction_id(tron, tx_id, timeout=120, poll_latency=0.1):
    with Timeout(timeout) as _timeout:
        while True:
            tx_detail = tron.trx.get_transaction(tx_id)
            # FIXME: The check for a null `ref_block_hash` is due to parity's
            if tx_detail is not None and \
                    'raw_data' in tx_detail and \
                    tx_detail['raw_data']['ref_block_hash'] is not None:
                break
            _timeout.sleep(poll_latency)
    return tx_detail
