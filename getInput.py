#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

STARTING, GETPK, GETMNEMONIC, ACCOUNTBAL, GETALCSTAT, TYPING_REPLY_2 = range(6)

reply_keyboard2 = [
    ['Mnemonic'],
    ['/Get_PK', '/Cancel']
]

reply_keyboard3 = [
    ['Private_key'],
    ['/GetMnemonic', '/Cancel']
]

reply_keyboard4 = [
    ['Public_key'],
    ['/Account_balance', '/Cancel']
]

reply_keyboard5 = [
    ['Public-Key'],
    ['/Get_account_status', '/Cancel']
]

reply_keyboard6 = [
    ['Buy_DMT2_TOKEN'],
    ['/Buy', '/Cancel']
]

reply_keyboard_category = [
    ['/Buy_DMT2', 'Get_PK', 'Account_balance'],
    ['GetMnemonic', 'Get_Alc_status', '/GetAlc'],
    ['/About', '/Help', '/Cancel', '/Main_Menu'],
]

reply_alternative = [
    ['/Get_PK', '/Account_balance'],
    ['/GetMnemonic', '/Get_Alc_status'],
    ['/Main_Menu'],
]

reply_keyboard_main = [
    ['/Buy_DMT2', '/Others'],
    ['/Cancel'],
]

markup_category = ReplyKeyboardMarkup(reply_keyboard_category, one_time_keyboard=True)
markup2 = ReplyKeyboardMarkup(reply_keyboard_main, one_time_keyboard=True)
markup3 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=True)
markup4 = ReplyKeyboardMarkup(reply_keyboard3, one_time_keyboard=True)
markup5 = ReplyKeyboardMarkup(reply_keyboard4, one_time_keyboard=True)
markup6 = ReplyKeyboardMarkup(reply_keyboard5, one_time_keyboard=True)
markup7 = ReplyKeyboardMarkup(reply_alternative, one_time_keyboard=True)

user_d = {}


def facts_to_str(user_data: Dict[str, str]) -> str:
    arg = list()

    for key, value in user_data.items():
        arg.append(f'{key} - {value}')

    return "\n".join(arg).join(['\n', '\n'])


def getMarkup(update, context, message, mark_up):
    update.message.reply_text(message, reply_markup=mark_up)


def main_menu(update, context):
    update.message.reply_text(
        "Select: ",
        reply_markup=markup2,
    )


def inputcateg(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Enter the following information",
        reply_markup=markup_category,
    )

    return STARTING


def init_choice(update, context) -> int:
    text = update.message.text
    if text == 'Get_PK' or text == '/Get_PK':
        update.message.reply_text(
            "Select",
            reply_markup=markup3,
        )
        return GETPK

    elif text == 'GetMnemonic' or text == '/GetMnemonic':
        update.message.reply_text(
            "Select",
            reply_markup=markup4,
        )
        return GETMNEMONIC

    elif text == 'Account_balance' or text == '/Account_balance':
        update.message.reply_text(
            "Select",
            reply_markup=markup5,
        )
        return ACCOUNTBAL

    elif text == 'Get_Alc_status' or text == '/Get_Alc_status':
        update.message.reply_text(
            "Select",
            reply_markup=markup6,
        )
        return GETALCSTAT


def otherwise(update, context):
    text = update.message.text
    expected = [
        'Mnemonic',
        'Private_key',
        'Public_key',
        'Public-Key',
        '/Mnemonic',
        '/Private_key',
        '/Public_key',
        '/Public-Key'
    ]
    for b in expected:
        if text == b:
            user_d[b] = text
            update.message.reply_text(f'Enter {text.lower()}?')

    return TYPING_REPLY_2


def response(update, context, mark_up, command):
    text = update.message.text
    update.message.reply_text(
        "I got this argument:\n"
        f"{text}\n"
        f"Now click /{command} to execute.",
        reply_markup=mark_up,
    )


def helper_func(
        update,
        context,
        category,
        text,
        markup,
        command
):

    user_d[category] = text
    response(update, context, markup, command)
    user_data = context.user_data
    user_data[category] = user_d[category]


def received_information_2(update, context):
    text = update.message.text
    for a in user_d:
        category = user_d[a]
        if category == 'Mnemonic':
            helper_func(update, context, category, text, markup3, "Get_PK") #"Wrong Mnemonic", GETPK)
            return GETPK

        elif category == 'Private_key' and len(text) > 58:
            helper_func(update, context, category, text, markup4, "GetMnemonic") #"Invalid Private Key", GETMNEMONIC)
            return GETMNEMONIC

        elif category == 'Public_key' and len(text) == 58:
            helper_func(update, context, category, text, markup5, "Account_balance") #"Invalid Public Key", ACCOUNTBAL)
            return ACCOUNTBAL

        elif category == 'Public-Key' and len(text) == 58:
            helper_func(update, context, category, text, markup6, "Get_account_status") #"Invalid Public Key", GETALCSTAT)
            return GETALCSTAT

    user_d.clear()
    return TYPING_REPLY_2


# Returns to main menu
def menuKeyboard(update, context):
    update.message.reply_text('Select')
    inputcateg(update, context)
    return STARTING


def alternative(update, context):
    update.message.reply_text("Navigate with command:", reply_markup=markup7)


def done(update: Update, context: CallbackContext):
    return ConversationHandler.END
