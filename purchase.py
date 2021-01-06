#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext
from buyToken import buy_token

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard1 = [
    ['Public_key', 'Quantity'],
    ['Secret_Key', 'Note'],
    ['/Done'],
    ['/Main_menu'],
]
markup2 = ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=True)
user_d = {}


def facts_to_str(user_data: Dict[str, str]) -> str:
    """
    Takes the user_data object, strips context into a list
    :param user_data:
    :return: Formated key-pair
    """
    arg = list()

    for key, value in user_data.items():
        arg.append(f'{key} - {value}')

    return "\n".join(arg).join(['\n', '\n'])


def args(update: Update, context: CallbackContext) -> int:
    """
    Entry point for taking arguments from user
    :param update:
    :param context:
    :return: The next line of action.
    """
    update.message.reply_text(
        "Enter the following information",
        reply_markup=markup2,
    )

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    """
    Compares supplied information to match what we expect.
    Passes it to DB if true.
    :param update:
    :param context:
    :return: The next line of action.
    """
    expected = ['Public_key', 'Quantity', 'Secret_Key', 'Note']
    text = update.message.text
    for b in expected:
        if text == b:
            user_d[b] = text
            update.message.reply_text(f'Enter {text.lower()}?')

    return TYPING_REPLY


def received_information(update: Update, context: CallbackContext) -> int:
    """
    Displays received arguments and passed it to temp_database
    :param update:
    :param context:
    :return: int (the next line of action)
    """
    text = update.message.text
    for a in user_d:
        category = user_d[a]
        if category == 'Public_Key' and len(text) == 58:
            assert len(text) == 58, update.message.reply_text("The address is invalid address")
            user_d[category] = text
        elif category == 'Quantity' and type(int(text) == int):
            user_d[category] = int(text)
        elif category == 'Secret_Key' and len(text) > 58:
            user_d[category] = text
        else:
            user_d[category] = text
        user_data = context.user_data
        user_data[category] = user_d[category]

    update.message.reply_text(
        "I got this from you:\n"
        f"{facts_to_str(user_d)}",
        reply_markup=markup2,
    )
    user_d.clear()

    return CHOOSING


def done(update: Update, context: CallbackContext):
    """
    Escape-exec func
    :param update:
    :param context:
    :return: Returns from buy_token()
    """
    buy_token(update, context)
