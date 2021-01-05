#!/usr/bin/env python
# -*- coding: utf-8 -*-

from algosdk import account, mnemonic
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
# from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from client import connect
from getInput import *
import time

algod_client = connect(None, None)


def create_account(update, context):
    """
    Create new public/private key pair
    Returns the result of generating an account to user:
    :param update:
    :param context:
    :return: 1). An Algorand address, 2). A mnemonic seed phrase
    """
    update.message.reply_text("Hang on while I get you an account ...")
    time.sleep(1)
    try:
        sk, pk = account.generate_account()
        if not (pk and sk is None):
            update.message.reply_text("Account creation success.\nYour address:  {}\n"
                                      "Private Key:  {}\n\n"
                                      "Keep your mnemonic phrase from prying eyes.\n"
                                      "I do not hold or manage your keys."
                                      "".format(pk, sk)
                                      )
            context.user_data['default_pk'] = pk
        else:
            update.message.reply_text('Account creation error\n\n.')
            # return ConversationHandler.END
        update.message.reply_text('To test if your address works fine, copy your address, and visit:\n ')
        keyboard = [[InlineKeyboardButton(
            "DISPENSER", 'https://bank.testnet.algorand.network/', callback_data='1')]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('the dispenser to get some Algos\nSession ended.'
                                  'Click /start to begin.', reply_markup=reply_markup)
    except Exception as e:
        return e
    return STARTING


# Generate mnemonic words - 25 Algorand-type seed phrase
def get_mnemonics_from_sk(update, context):
    """
    Takes in private key and converts to mnemonics
    :param context:
    :param update:
    :return: 25 mnemonic words
    # """
    if 'Private_key' in context.user_data:
        sk = context.user_data['Private_key']
        phrase = mnemonic.from_private_key(str(sk))
        update.message.reply_text(
            "Your Mnemonics:\n {}\n\nKeep your mnemonic phrase from prying eyes.\n"
            "\nI do not hold or manage your keys.".format(phrase), reply_markup=markup_category
        )
        update.message.reply_text('\nSession ended.')
        del context.user_data['Private_key']
    else:
        update.message.reply_text("Key not found")
        return ConversationHandler.END
    return STARTING


def query_balance(update, context):
    """
    Check balance on an account's public key
    :param update:
    :param context:
    :return: Balance in account plus asset (s) balance
    """
    if 'Public_key' in context.user_data:
        pk = context.user_data['Public_key']
        update.message.reply_text("Getting the balance on this address ==>   {}.".format(pk))
        if len(pk) == 58:
            account_bal = algod_client.account_info(pk)
            bal = account_bal['amount']
            update.message.reply_text("Balance on your account: {}".format(bal), reply_markup=markup_category)
            for k in account_bal['assets']:
                update.message.reply_text(f"Asset balance: {k['amount']}, Asset ID: {k['asset-id']}\nClick /Menu"
                                          f" to go the main menu.")
            menuKeyboard(update, context)
        else:
            update.message.reply_text("Wrong address supplied.\nNo changes has been made.")
            return menuKeyboard(update, context)
    else:
        update.message.reply_text("Cannot find public key")
        menuKeyboard(update, context)
    return STARTING


def getPK(update, context):
    """
    Takes in 25 mnemonic and converts to private key
    :param context:
    :param update:
    :return: 25 mnemonic words
    # """
    if 'Mnemonic' in context.user_data:
        mn = context.user_data['Mnemonic']
        phrase = mnemonic.to_private_key(str(mn))
        update.message.reply_text(
            "Your Private Key:\n {}\n\nKeep your key from prying eyes.\n"
            "\n\nI do not hold or manage your keys.".format(phrase), reply_markup=markup_category
        )
        update.message.reply_text('\nSession ended.')
        del context.user_data['Mnemonic']
    else:
        update.message.reply_text("Cannot find Mnemonic.")
        return ConversationHandler.END
    return STARTING


def getAddress(update, context):
    if 'default_pk' in context.user_data:
        addr = context.user_data['default_pk']
        update.message.reply_text("Did you mean this? \n {}".format(addr), reply_markup=markup_category)
        # return ConversationHandler.END
    else:
        update.message.reply_text(
            "I don't have a record of your address\n"
            "Maybe you should create or supply one."
        )
        return ConversationHandler.END
    return STARTING
