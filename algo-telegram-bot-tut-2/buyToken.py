#!/usr/bin/env python
# -*- coding: utf-8 -*-

from algosdk.future.transaction import transaction
from algosdk import mnemonic
from waitforconfirmation import wait_for_confirmation
from algosdk.future.transaction import AssetTransferTxn
from client import connect
from getInput import markup2
from optIn import optin
import logging
import os
from dotenv import load_dotenv
from telegram.ext import ConversationHandler
import time

algod_client = connect(None, None)
load_dotenv()
price_progress = [1000, ]  # Tracks price change
current_price = price_progress[-1]
saleable = 6000000  # Total asset available for IPO.
total_buy = 0
assetBalance = 0
asset_id = 13251912


# Don't expose sensitive information.
to = os.environ['DEFAULT2_ACCOUNT'] # getenv('DEFAULT2_ACCOUNT')
auth = os.environ['DEFAULT2_MNEMONTIC'] # getenv('DEFAULT2_MNEMONTIC')
rate = 30

# pull account information of supposedly contract account
accountInfo = algod_client.account_info(to)
successful = None


# Price updater.
# For every
def updatePrice(update, context):
    """
    Update the price after every 2000000 token is sold
        : price is increased by the
    half of the current price
    :param update:
    :param context:
    :return:
    """
    global rate
    global current_price

    if saleable >= 4000000:
        rate = rate
        current_price = current_price
        update.message.reply_text(
            "Current price per DMT2: {} MicroAlgo".format(current_price))
    elif 2000000 < saleable < 4000000:
        rate = 20
        newPrice = int(current_price + (current_price / 2))
        current_price = newPrice
        update.message.reply_text(
            "Current price per DMT2: {} MicroAlgo".format(newPrice))
    elif saleable <= 2000000:
        rate = 10
        newPrice = int(current_price + (current_price / 2))
        current_price = newPrice
        update.message.reply_text(
            "Current price per DMT2: {} MicroAlgo".format(newPrice))


def updateAssetBalance(update, context):
    """
    Continious update of asset balance in creator's account
    NB: We will need this for a check
    :param update:
    :param context:
    :return:
    """
    global assetBalance
    for i in accountInfo['assets']:
        if i['asset-id'] == asset_id:
            assetBalance = i['amount']
            break


def transfer(update, context, receiver, amount):
    """
    Transfer a custom asset from default account A to account B (Any)
    :param update: Default telegram argument
    :param context: Same as update
    :param sender: Sender of this transaction
    :param receiver: The beneficiary of the asset in transit
    :param amount: Amount in custom asset other than ALGO
    :return:
    """
    global saleable
    params = algod_client.suggested_params()
    params.fee = 1000
    params.flat_fee = True
    print(auth)
    try:
        assert saleable >= amount, response_end(
            update, context, "Sales for the period is exhausted")

        txn = AssetTransferTxn(
            sender=to,  # asset_manage_authorized,
            sp=params,
            receiver=receiver,
            amt=int(amount),
            index=asset_id
        )
        # Sign the transaction
        sk = mnemonic.to_private_key(auth)
        signedTrxn = txn.sign(sk)

        # Submit transaction to the network
        tx_id = algod_client.send_transaction(signedTrxn)
        message = "Successful! \nTransaction hash: {}.".format(tx_id)
        wait_for_confirmation(update, context, algod_client, tx_id)
        logging.info(
            "...##Asset Transfer... \nReceiving account: {}.\nMessage: {}\nOperation: {}\nTxn Hash: {}"
            .format(receiver, message, transfer.__name__, tx_id))

        update.message.reply_text(message, reply_markup=markup2)
        saleable -= amount
        # Erase the key soon as you're done with it.
        context.user_data.clear()
    except Exception as err:
        print(err)
    return markup2


def response_end(update, context, message):
    """
    Update the user with response with recourse to the executing function
    :param update:
    :param context:
    :param message: Message to forward to user --> str
    :return:
    """
    update.message.reply_text(message, reply_markup=markup2)
    return ConversationHandler.END


def buy_token(update, context):
    """
    Purchase an ASA: This function handles the whole computations, takes
    payment from the user and forward token remission to "transfer()"
    :param update:
    :param context:
    :return:
    """
    # Request to modify global variables. Peculiar to
    # Python 3 or newer.
    global successful
    global current_price
    global price_progress
    global rate

    updatePrice(update, context)
    updateAssetBalance(update, context)

    update.message.reply_text("Broadcasting transaction...")

    # Extracts the arguments from the temp_DB
    user_data = context.user_data
    buyer = user_data["Public_key"]
    qty = user_data["Quantity"]
    sk = user_data["Secret_Key"]
    note = user_data["Note"].encode()

    # Firstly, opt in user if not already subscribe to DMT2 asset.
    optin(update, context, buyer, sk)
    time.sleep(3)
    max_buy = 500000  # Instant purchase pegged to 500,000 DMT2

    # If there is enough token to sell
    # Perform other necessary checks, then execute if all passed.

    try:
        if saleable > 0:
            params = algod_client.suggested_params()
            fee = params.fee = 1000
            flat_fee = params.flat_fee = True
            amountToPay = int(current_price * qty)
            alcBal = algod_client.account_info(buyer)['amount']
            assert alcBal > amountToPay, response_end(update, context, "Not enough balance.")
            assert qty <= max_buy, response_end(update, context, "Max amount per buy is restricted to 500000 DMT2.")
            assert qty >= 500, response_end(
                update, context, "Minimum buy is 500 DMT2.\n Session ended.")
            assert len(buyer) == 58, response_end(update, context,
                                                  "Incorrect address")

            raw_trxn = transaction.PaymentTxn(sender=buyer,
                                              fee=fee,
                                              first=params.first,
                                              last=params.last,
                                              gh=params.gh,
                                              receiver=to,
                                              amt=amountToPay,
                                              close_remainder_to=None,
                                              note=note,
                                              gen=params.gen,
                                              flat_fee=flat_fee,
                                              lease=None,
                                              rekey_to=None)

            # Sign the transaction
            signedTrxn = raw_trxn.sign(sk)
            update.message.reply_text("Just a second.....")
            # Submit transaction to the network
            tx_id = algod_client.send_transaction(signedTrxn)
            message = "Transaction hash: {}.".format(tx_id)
            wait = wait_for_confirmation(update, context, algod_client, tx_id)
            logging.info(
                "...##Asset Transfer... \nReceiving account: {}.\nMessage: {}\nOperation: {}\n"
                .format(buyer, message, buy_token.__name__))
            successful = bool(wait is not None)

            if successful:
                amountToSend = qty + (qty * (rate / 100))
                update.message.reply_text(
                    f"Payment success...\nTransferring {amountToSend} token to address... --> {buyer}",
                    reply_markup=markup2
                )
                transfer(update, context, buyer, amountToSend)
            else:
                response_end(update, context, "Transaction declined")
        else:
            update.message.reply_text("Token unavailable at the moment", reply_markup=markup2)

    except Exception as err:
        logging.info("Error encountered: ".format(err))
        update.message.reply_text("Something went wrong1\nTransaction Unsuccessful", reply_markup=markup2)

