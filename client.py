#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from algosdk.v2client import algod
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
from getInput import reply_keyboard_category

load_dotenv()
ALGODTOKEN = os.getenv('ALGODTOKEN')


"""Keyboard/menu parameters : passed to the CommandHandler object"""

markup = ReplyKeyboardMarkup(reply_keyboard_category, one_time_keyboard=True)


def connect(update, context):
    """
    Connect to an algorand node
    :param update:
    :param context:
    :return:
    """
    url = os.getenv('URL')  # Serve the endpoint to client node (https://purestake.com)
    algod_token = ALGODTOKEN   # Your personal token (https://purestake.com)
    headers = {"X-API-Key": algod_token}
    try:
        return algod.AlgodClient(algod_token, url, headers)
    except Exception as e:
        update.message.reply_text("Something went wrong.\nCould not connect to a node at this time.")
