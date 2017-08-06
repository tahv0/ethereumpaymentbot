#!/usr/bin/env python

import logging
from pprint import pprint
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
from telegram.ext import Updater, CommandHandler
from config_parser.config_parser import get_config_value
from sqlalchemy.orm import subqueryload
from db.models import Chat, Session, Account


class TGBot:
    def __init__(self):
        updater = Updater(token=get_config_value('TGBOT', 'token'))
        dispatcher = updater.dispatcher
        start_handler = CommandHandler('start', self.__start)
        account_add_handler = CommandHandler('add', self.__add_account, pass_args=True)
        help_handler = CommandHandler('help', self.__help)
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(account_add_handler)
        dispatcher.add_handler(help_handler)
        updater.start_polling()

    def __start(self, bot, update):
        self.__check_and_add_chat(update)
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text="<pre>Hello! I'm Ethereum Payment Bot. "
                                                          "You can Subscribe nodifications from me about balance changes in blockchain for wanted Ethereum"
                                                          " wallets!</pre>"
                                               "<pre>Please use /help for showing all I can do for you!</pre>",
                         parse_mode='HTML'
                         )

    def __add_account(self, bot, update, args):
        self.__check_and_add_chat(update)
        session = Session()
        chat_id = update.message.chat_id
        chat = session.query(Chat).options(subqueryload(Chat.accounts)).filter_by(id=chat_id).one()
        if not args:
            return self.__help(bot, update)
        for arg in args:
            account = session.query(Account).filter_by(id=arg).one_or_none()
            account_subscribed = list(filter(lambda x: x.id == arg, chat.accounts))
            if account is None and not account_subscribed:
                chat.accounts.append(Account(id=arg))
                session.commit()
            if account is not None and not account_subscribed:
                chat.accounts.append(account)
                session.commit()
        session.close()
        bot.send_message(chat_id=chat_id, text="Account(s) added!")

    def __check_and_add_chat(self,  update):
        session = Session()
        chat_id = update.message.chat_id
        old_chat = session.query(Chat).filter_by(id=chat_id).one_or_none()
        if old_chat is None:
            session.add(Chat(id=chat_id))
            session.commit()
        session.close()

    def __help(self, bot, update):
        chat_id = update.message.chat_id
        # TODO: Implement missing handlers defined in help_text
        help_text = "Usage:\n" \
                    "# subscribe nodifications for wallets\n" \
                    "`/add` <wallet1>  <wallet2>\n" \
                    "# remove subscriptions from wallets\n" \
                    "`/remove` <wallet1>  <wallet2>\n" \
                    "# show your current subscriptions\n" \
                    "`/subscriptions`\n" \
                    "# activate nodifications. Doesn't resend missed payments\n" \
                    "`/activate`\n" \
                    "# deactivate nodifications from all subscribed addresses\n" \
                    "`/deactivate`\n" \
                    "# print help text\n" \
                    "`/help`"
        bot.send_message(chat_id=chat_id, text=help_text, parse_mode="Markdown")



