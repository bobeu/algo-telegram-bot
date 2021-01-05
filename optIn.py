#!/usr/bin/env python
# -*- coding: utf-8 -*-

from client import connect
import logging
from algosdk.future.transaction import AssetTransferTxn
from waitforconfirmation import wait_for_confirmation
import time

asset_id = 13251912


# First time account to opt in for DMT2 asset
def optin(update, context, recipient, sk):
    algod_client = connect(update, context)
    params = algod_client.suggested_params()
    # Check if recipient holding DMT2 asset prior to opt-in
    account_info_pk = algod_client.account_info(recipient)
    print(account_info_pk)
    holding = None
    # idx = 0
    for assetinfo in account_info_pk['assets']:
        scrutinized_asset = assetinfo['asset-id']
        # idx = idx + 1
        if asset_id == scrutinized_asset:
            holding = True
            msg = "This address has opted in for DMT2, ID {}".format(asset_id)
            logging.info("Message: {}".format(msg))
            logging.captureWarnings(True)
            break
    if not holding:
        # Use the AssetTransferTxn class to transfer assets and opt-in
        txn = AssetTransferTxn(sender=recipient,
                               sp=params,
                               receiver=recipient,
                               amt=0,
                               index=asset_id)
        # Sign the transaction
        # Firstly, convert mnemonics to private key.
        # For tutorial purpose, we will focus on using private key
        # sk = mnemonic.to_private_key(seed)
        sendTrxn = txn.sign(sk)

        # Submit transaction to the network
        txid = algod_client.send_transaction(sendTrxn)
        message = "Transaction was signed with: {}.".format(txid)
        wait = wait_for_confirmation(update, context, algod_client, txid)
        time.sleep(2)
        hasOptedIn = bool(wait is not None)
        if hasOptedIn:
            update.message.reply_text(f"Opt in success\n{message}")

        return hasOptedIn
