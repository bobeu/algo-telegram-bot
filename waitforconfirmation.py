#!/usr/bin/env python
# -*- coding: utf-8 -*-

from client import connect

algod_client = connect(None, None)


def wait_for_confirmation(update, context, client, txid):
    """
    Utility function to wait until the transaction is
    confirmed.
    :param update:
    :param context:
    :param client: Connection info i.e request obj
    :param txid: Hash/acknowledged receipt of the current broadcasted transaction
    :return: pending transaction.
    """
    last_round = algod_client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    update.message.reply_text("Waiting for confirmation...")
    while not (txinfo.get('confirmed-round')
               and txinfo.get('confirmed-round') > 0):
        last_round += 1
        txinfo = algod_client.pending_transaction_info(txid)
    return txinfo
