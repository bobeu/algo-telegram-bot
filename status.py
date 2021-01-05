#!/usr/bin/env python
# -*- coding: utf-8 -*-

from waitforconfirmation import algod_client
from getInput import markup_category, inputcateg, STARTING


def account_status(update, context):
    """
    :param update: Telegram's default param
    :param context: Telegram's default param
    :param address: 32 bytes Algorand's compatible address
    :return: Address's full information
    """
    try:
        if 'Public-Key' in context.user_data:
            pk = context.user_data['Public-Key']
            status = algod_client.account_info(pk)
            for key, value in status.items():
                update.message.reply_text("{} : {}".format(key, value), reply_markup=markup_category)
        return STARTING
    except Exception as e:
        update.message.reply_text("Something went wrong.\nProbably I cannot find any key.\n"
                                  "Re /start and create an account or supply your public key "
                                  "if you have one.")