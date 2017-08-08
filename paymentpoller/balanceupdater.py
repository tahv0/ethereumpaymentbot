#!/usr/bin/env python
import requests
from datetime import datetime
from config_parser.config_parser import get_config_value
from db.models import AccountBalance, Account, Session
from sqlalchemy.orm import eagerload

def update_accounts_balances(tgbot):
    config_json_rpc_api_url = get_config_value('BLOCKCHAINPOLLER', 'json_rpc_api_url')
    config_json_rpc_api_port = int(get_config_value('BLOCKCHAINPOLLER', 'json_rpc_api_port'))
    json_rpc_api_url = 'localhost' if config_json_rpc_api_url is None else config_json_rpc_api_url
    json_rpc_api_port = 8545 if config_json_rpc_api_port is None else config_json_rpc_api_port
    try:
        ether_stock_price_request = requests.get('https://api.coinmarketcap.com/v1/ticker/ethereum/?convert=EUR')
        ether_stock_price = ether_stock_price_request.json()[0]
    except (requests.ConnectionError, IndexError):
        return
    else:
        if ether_stock_price_request.status_code != 200:
            # try next time if there is network error
            return
    session = Session()
    accounts_queryset = session.query(Account).options(eagerload(Account.chats)).all()
    for account in accounts_queryset:
        post_json = {'jsonrpc': '2.0', 'method': 'eth_getBalance', 'params': ['{}'.format(account.id), 'latest'], 'id': 1}
        account_balance = requests.post('http://{}:{}'.format(json_rpc_api_url, json_rpc_api_port), json=post_json).json()
        old_balance = session.query(AccountBalance).filter_by(account_id=account.id).order_by(AccountBalance.id.desc()).first()
        if 'error' not in account_balance:
            new_balance = int(account_balance['result'], 16)
            if old_balance is None or new_balance != old_balance.balance:
                changed_value = new_balance if old_balance is None else (new_balance - old_balance.balance) / 10 ** 18
                changed_in_money = {
                    'EUR': changed_value * float(ether_stock_price['price_eur']),
                    'USD': changed_value * float(ether_stock_price['price_usd'])
                }
                new_account_balance = AccountBalance(account_id=account.id,
                                                     balance=new_balance,
                                                     change_in_money=changed_in_money)
                session.add(new_account_balance)
                session.commit()
                if old_balance is not None:
                    for chat in account.chats:
                        if chat.subscription_active:
                            tgbot.send_message(chat_id=chat.id, text='{} UTC - 1 ETH = ${} / €{}\n'
                                                                     'Account {} balance changed {} ETH.\n'
                                                                     'Value ${} / €{}'
                                               .format(
                                                str(datetime.utcnow()),
                                                round(float(ether_stock_price['price_usd']), 2),
                                                round(float(ether_stock_price['price_eur']), 2),
                                                account.id,
                                                changed_value,
                                                round(changed_in_money["USD"], 3),
                                                round(changed_in_money["EUR"], 3)))
    session.close()

