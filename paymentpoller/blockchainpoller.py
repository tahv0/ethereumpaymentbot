#!/usr/bin/env python
import time
from config_parser.config_parser import get_config_value
from paymentpoller.balanceupdater import update_accounts_balances
from paymentpoller.tgbotupdater import TGBotUpdater
import telegram
tgbot_updater = TGBotUpdater()
tgbot = telegram.Bot(token=get_config_value('TGBOT', 'token'))

def start_polling():
    try:
        while True:
            update_accounts_balances(tgbot)
            config_timeout_seconds = get_config_value('BLOCKCHAINPOLLER', 'timeout_seconds')
            timeout_seconds = 60 if config_timeout_seconds is None else int(config_timeout_seconds)
            time.sleep(timeout_seconds)
    except ValueError as e:
        print('You fucked up BLOCKCHAINPOLLER.timeout_seconds setting in conf file...')
        raise e
    except KeyboardInterrupt:
        pass