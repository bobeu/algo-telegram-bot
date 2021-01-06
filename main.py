#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from status import account_status
from buyToken import *
from getInput import *
from purchase import *

from generateAccount import (
    create_account,
    get_mnemonics_from_sk,
    query_balance,
    getPK,
    getAddress
)
import os
import logging
from dotenv import load_dotenv

from telegram.ext import (Updater, CommandHandler, Filters,
                          ConversationHandler, PicklePersistence,
                          CallbackContext, MessageHandler)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv('TOKEN')  # environ.get('BOT_TOKEN')  # Token from the bot father
updateAssetBalance(None, None)


def start(update, context: CallbackContext):
    """
    Gives direction for use
    Displays information about the bot and available commands
    :param update:
    :param context:
    :return: None
    """
    user = update.message.from_user
    reply = "Hi {}!\nI am ALGOMessenger.\n".format(user['first_name'])
    reply += (
        " Here are what you can do with this Algobot20.\n\n"
        "* /GetAlc - Create an account.\n"
        "* Get Mnemonic words from Private Key.\n"
        "* Check your account balance.\n"
        "* Buy DMT2 Token (Algorand Standard Asset.\n"
        "* Converts Mnemonic to Private key\n"
        "* Check account status.\n"
        "* Get your account public key (if you have created one with this bot.\n\n"
        "/About - about us.\n"
        "/Help - if you need help.\n"
        "/Cancel - ends a conversation.\n\n"
        "Navigate to /Main_menu to sub section."
    )
    update.message.reply_text(reply, reply_markup=markup)
    context.user_data.clear()


# Returns about us
def aboutUs(update, context):
    """
    Read more about Algorand and how you can build on Algorand
    :param update:
    :param context:
    :return: None
    """
    keyboard = [[
        InlineKeyboardButton("Website",
                             'https://algorand.com',
                             callback_data='1'),
        InlineKeyboardButton("Developer'site",
                             'https://developer.algorand.org',
                             callback_data='2')
    ],
        [
            InlineKeyboardButton("Community",
                                 'https://community.algorand.com',
                                 callback_data='3')
        ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Learn more about Algorand:',
                              reply_markup=reply_markup)


# Need help?
def help_command(update, context):
    """
    Gives direction for use
    :param update:
    :param context:
    :return: None
    """
    update.message.reply_text("Use /start to test this bot.")


def cancel(update, context):
    """
    Terminates a session and keeps the bot unengaged
    :param update:
    :param context:
    :return: int --> Ends the session
    """
    update.message.reply_text(f"All information is erased:", reply_markup=markup2)
    context.user_data.clear()
    start(update, context)
    return ConversationHandler.END


def main():
    """
    The heart of the bot.
    Keeps track of how program should run.
    Here you specify the token gotten from the BotFather,
    i.e the token for your bot. NB: Keep it secret.

    Updater class employs the telegram.ext.Dispatcher and
    provides a front-end to the bot for the users.
    So, you only need to focus on backend side.

    The ConversationHandler holds a conversation with a single
     user by managing four collections of other handlers
    :return:
    """
    # Create the Updater and pass it your bot's token.
    pp = PicklePersistence(filename='reloroboty')
    updater = Updater(TOKEN, persistence=pp, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    cul_handler = ConversationHandler(
        entry_points=[CommandHandler('Buy_DMT2', args)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(Public_key|Quantity|Secret_Key|Note)$'),
                    regular_choice), CommandHandler('Done', buy_token)
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text
                    & ~(Filters.command | Filters.regex('^Done$')),
                    regular_choice)
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text
                    & ~(Filters.command | Filters.regex('^Done$')),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('Others', inputcateg)],
        states={
            STARTING: [
                MessageHandler(Filters.regex('^(GetMnemonic|Account_balance|Get_Alc_status|Get_PK)$'),
                               init_choice)
            ],

            GETPK: [
                MessageHandler(
                    Filters.regex('^(Mnemonic)$'), otherwise), CommandHandler('Get_PK', getPK)
            ],
            GETMNEMONIC: [
                MessageHandler(
                    Filters.regex('^(Private_key)$'), otherwise),
                CommandHandler('GetMnemonic', get_mnemonics_from_sk)
            ],
            ACCOUNTBAL: [
                MessageHandler(
                    Filters.regex('^(Public_key)$'), otherwise),
                CommandHandler('Account_balance', query_balance)
            ],

            GETALCSTAT: [
                MessageHandler(
                    Filters.regex('^(Public-Key)$'), otherwise),
                CommandHandler('Get_account_status', account_status)
            ],

            TYPING_REPLY_2: [
                MessageHandler(
                    Filters.text
                    & ~(Filters.command | Filters.regex('^Done$')),
                    received_information_2,
                )
            ],
        },
        fallbacks=[CommandHandler('Done', done)],
    )

    dp.add_handler(cul_handler)
    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('Others', inputcateg))
    dp.add_handler(CommandHandler('GetAlc', create_account))
    dp.add_handler(CommandHandler('Cancel', cancel))
    dp.add_handler(CommandHandler('About', aboutUs))
    dp.add_handler(CommandHandler('Help', help_command))
    dp.add_handler(CommandHandler('Main_menu', main_menu))
    dp.add_handler(CommandHandler('Get_My_Address', getAddress))
    dp.add_handler(CommandHandler('Account_balance', inputcateg))
    dp.add_handler(CommandHandler('Get_Alc_status', inputcateg))
    dp.add_handler(CommandHandler('GetMnemonic', inputcateg))
    dp.add_handler(CommandHandler('Get_PK', inputcateg))
    dp.add_handler(CommandHandler('Others', inputcateg))
    dp.add_handler(CommandHandler('Buy_DMT2', args))


    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
