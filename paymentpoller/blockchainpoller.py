#!/usr/bin/env python
import time, sys
from datetime import datetime
from config_parser.config_parser import get_config_value
from paymentpoller.balanceupdater import update_accounts_balances
from paymentpoller.tgbotupdater import TGBotUpdater
import telegram
tgbot_updater = TGBotUpdater()
tgbot = telegram.Bot(token=get_config_value('TGBOT', 'token'))

def start_polling():
    print(str(datetime.utcnow()), 'STARTED')
    try:
        while True:
            update_accounts_balances(tgbot)
            config_timeout_seconds = get_config_value('BLOCKCHAINPOLLER', 'timeout_seconds')
            timeout_seconds = 60 if config_timeout_seconds is None else int(config_timeout_seconds)
            time.sleep(timeout_seconds)
    except ValueError as e:
        # TODO: json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
        #     ether_stock_price = ether_stock_price_request.json()[0]
        print('You fucked up BLOCKCHAINPOLLER.timeout_seconds setting in conf file...')
        print(str(e))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(str(e))
    finally:
        tgbot_updater.stop_polling()
