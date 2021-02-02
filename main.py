```
# !/usr/bin/env python
# -*- coding: utf-8 -*-

# Import the necessary modules.

import logging
from algosdk import account, mnemonic
from connection import algod_client
from telegram import (ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup)
import os

from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    Filters,
    ConversationHandler,
    PicklePersistence,
)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Use the token you got from bot father here
TOKEN = < YOUR_BOT_TOKEN_HERE >

# Displays these as commands when the start command is invoked
# Also, a way of grabbing input from the user
reply_keyboard = [
    ['/Create_account', '/Get_Mnemonics_from_pky'],
    [
        '/Query_account_balance',
        '/Account_status', '/enquire'
    ],
    ['/About', '/help', '/Done'],
]

# Maps the above parameters to the keyboard, so when user clicks
# on any, it is captured as command
# Set the one-time keyboard to true.
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


# Utility that instantiates conversation with the bot
# Must pass in "update" and "context as parameters to every declared/defined functions
# update.message.from_user gets all updates from a user including name and username in Json object, so we are stripping off the user's username.

# 'context.user_data' temporarily stores all entries from user. It can be used as a way
# to collect input from users. It is always in Json format.
# Here we clear the user_data storage to ensure that we are not using existing data in
# place of current one since we will mostly be working with current data. So each time a
# user restarts the bot, we have an empty dictionary.
# update.message.reply_text() forwards updates to the user.
# If you need to send data types other than string, you should
# type-cast or wrap it in curly braces or directly convert it to string.

# This is called when the /start command is invoked
def start(update, context):
    user = update.message.from_user
    reply = "Hi {}! I am ALGOMessenger.".format(user['first_name'])
    reply += (
        "I can help you with a few things.\n"
        "Tell me what you need to do.\n"
        "They should be from the menu.\n"
        "Alert!\nYou should create an account first before running other functions.\nElse:"
        "If you can supply the keys if you have created a Testnet account before now. "
        "\nSend: \n"
        "/Create_account to get a new account.\n"
        "/Get_Mnemonic_from_pky imports Mnemonic from private key.\n"
        "/Balance to check the balances on your account.\n"
        "/Account_status get information about your account.\n"
        "Send /Done to cancel current session with the bot."
        "Send /start to restart the main menu."
    )
    # Removes all updates from the
    # user-data object.
    update.message.reply_text(reply, reply_markup=markup)
    context.user_data.clear()


# A polite way of ending a session or chat.
def end_chat(update, context):
    update.message.reply_text(
        "Your current session is terminated.\n"
        "Click /start to restart."
    )
    return ConversationHandler.END


# Returns the status of an account when called
# When called, gets the users existing address
# and return the status of the account as
# at when called, then end the session.

def account_status(update, context):
    """
    :param update: Telegram default param
    :param context: Telegram default param
    :param address: 32 bytes Algorand's compatible address
    :return: Address's full information
    """
    pk = context.user_data['default_pk']
    status = algod_client.account_info(pk)
    for key, value in status.items():
        update.message.reply_text("{} : {}".format(key, value))

    return ConversationHandler.END


# Generates a private and public key and return them to the user.
# update.message.reply() sends message in text format to the user.
# On returning the keys to user, it informs them to get a testnet
# Algo for the purpose
# of testing this bot.

def create_account(update, context):
    """
    Returns the result of generating an account to user:
        - An Algorand address
        - A private key.
    """
    update.message.reply_text(
        "Hang on while I get you an account ..."
    )
    sk, pk = account.generate_account()
    update.message.reply_text("Your address:   {}\nPrivate Key:    {}\n".format(pk, sk))
    update.message.reply_text(
        "Keep your mnemonic phrase from prying eyes.\n"
        "\nI do not hold or manage your keys."
    )
    # Stores the keys in the user_data obj.
    # Normally, you dont want to do this.

    context.user_data['default_sk'] = sk
    context.user_data['default_pk'] = pk
    if context.user_data.get('default_pk') == pk and context.user_data['default_sk'] == sk:
        update.message.reply_text("Account creation success.")
    else:
        update.message.reply_text('Account creation error\n.')

    update.message.reply_text('To test if your address works fine, copy your address, and visit:\n ')
    keyboard = [[InlineKeyboardButton(
        "DISPENSER", 'https://bank.testnet.algorand.network/', callback_data='1')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('the dispenser to get some Algos', reply_markup=reply_markup)

    update.message.reply_text("Session ended. Click /start to begin.")
    return ConversationHandler.END


# Function to convert private key to mnemonic phrase
def get_mnemonics_from_sk(update, context):
    """
    Takes in private key and converts to mnemonics
    :param context:
    :param update:
    :return: 25 mnemonic words
    # """
    # Search and pull for the key in the user_data
    sk = context.user_data['default_sk']
    phrase = mnemonic.from_private_key(sk)
    update.message.reply_text(
        "Your Mnemonics:\n {}\n\nKeep your mnemonic phrase from prying eyes.\n"
        "\n\nI do not hold or manage your keys.".format(phrase), reply_markup=markup
    )
    update.message.reply_text('\nSession ended.')
    return ConversationHandler.END


# Check user s account and return the current total balance with
# pending rewards.
# When called. it takes user's existing account address, performs
# the query operation
# and return the result to user.

def query_balance(update, context):
    pk = context.user_data['default_pk']
    update.message.reply_text(
        "Getting the balance on this address:   {}.".format(pk)
    )
    if len(pk) == 58:
        account_bal = algod_client.account_info(pk)['amount']
        update.message.reply_text(
            "Balance on your account: {}".format(account_bal)
        )
    else:
        update.message.reply_text("Wrong address supplied.\nNo changes has been made.")
        context.user_data.clear()
    return ConversationHandler.END


# Inline bot utility, can be used for polling, links etc.
def enquire(update, context):
    keyboard = [
        [InlineKeyboardButton(
            "Website", 'https://algorand.com', callback_data='1'
        ), InlineKeyboardButton("Developer'site", 'https://developer.algorand.org', callback_data='2')
        ],
        [InlineKeyboardButton("Community", 'https://community.algorand.com', callback_data='3')
         ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        'Learn more about Algorand:',
        reply_markup=reply_markup
    )


# help() provides guide when user needs help.
def help_command(update, context):
    update.message.reply_text("Use /start to test this bot.")


# On completion of a task, it clears the context and end the session.

def done(update, context):
    if 'choice' in context.user_data:
        del context.user_data['choice']
        context.user_data.clear()
        return ConversationHandler.END
    update.message.reply_text(
        "Swift! Your transaction is completed,",
        reply_markup=markup
    )
    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bots token.
    # can be any valid name.
    pp = PicklePersistence(filename= < specify a name for here> )
    updater = Updater( <Token from Bot Father here>, persistence = pp, use_context = True)

    # Get the dispatcher to register handlers
    # and handles the front-end
    dp = updater.dispatcher

    # For example, sending a /start command triggers the
    # 'start' function
    # This is done using the Commandhandler module.
    # When using the CommandHandler function, omit the back slash, otherwise
    # it throws.

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler(
        'Create_account', create_account)
    )
    dp.add_handler(CommandHandler(
        'Get_Mnemonics_from_pky', get_mnemonics_from_sk
    ))
    dp.add_handler(CommandHandler(
        'Query_account_balance', query_balance)
    )
    dp.add_handler(CommandHandler('Account_status', account_status))
    dp.add_handler(CommandHandler('Done', end_chat))
    dp.add_handler(CommandHandler('About', enquire))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('enquire', enquire))

    # Starts the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process
    # receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the
    # bot gracefully.

    updater.idle()


if __name__ == '__main__':
    main()
