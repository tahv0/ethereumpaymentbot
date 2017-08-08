#!/usr/bin/env python

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
from telegram.ext import Updater, CommandHandler
from config_parser.config_parser import get_config_value
from sqlalchemy.orm import eagerload
from db.models import Chat, Session, Account


class TGBotUpdater:
    def __init__(self):
        updater = Updater(token=get_config_value('TGBOT', 'token'))
        dispatcher = updater.dispatcher
        start_handler = CommandHandler('start', self._start)
        account_add_handler = CommandHandler('add', self._add_account, pass_args=True)
        account_rm_hanlder = CommandHandler('rm', self._rm_account, pass_args=True)
        deactivate_chat_handler = CommandHandler('deactivate', self._deactivate_chat)
        activate_chat_handler = CommandHandler('activate', self._activate_chat)
        subscriptions_handler = CommandHandler('subscriptions', self._get_subscriptions)
        help_handler = CommandHandler('help', self._help)
        credits_handler = CommandHandler('credits', self._credits)
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(account_add_handler)
        dispatcher.add_handler(account_rm_hanlder)
        dispatcher.add_handler(deactivate_chat_handler)
        dispatcher.add_handler(activate_chat_handler)
        dispatcher.add_handler(subscriptions_handler)
        dispatcher.add_handler(help_handler)
        dispatcher.add_handler(credits_handler)
        updater.start_polling()

    def _start(self, bot, update):
        self._check_and_add_chat(update)
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text="<pre>Hello! I'm Ethereum Payment Bot. "
                                                          "You can Subscribe notifications from me about balance changes in blockchain for wanted Ethereum"
                                                          " wallets!</pre>"
                                               "<pre>Please use /help for showing all I can do for you!</pre>",
                         parse_mode='HTML'
                         )

    def _add_account(self, bot, update, args):
        self._check_and_add_chat(update)
        session = Session()
        chat_id = update.message.chat_id
        chat = session.query(Chat).options(eagerload(Chat.accounts)).filter_by(id=chat_id).one()
        added_accounts = []
        if not args:
            return self._help(bot, update)
        for arg in args:
            account = session.query(Account).filter_by(id=arg).one_or_none()
            account_subscribed = list(filter(lambda x: x.id == arg, chat.accounts))
            if account is None and not account_subscribed:
                chat.accounts.append(Account(id=arg))
                session.commit()
                added_accounts.append(arg)
            elif not account_subscribed:
                chat.accounts.append(account)
                session.commit()
                added_accounts.append(arg)
        session.close()
        bot.send_message(chat_id=chat_id, text="{} Account(s) added!".format(len(added_accounts)))

    def _rm_account(self, bot, update, args):
        self._check_and_add_chat(update)
        session = Session()
        chat_id = update.message.chat_id
        chat = session.query(Chat).options(eagerload(Chat.accounts)).filter_by(id=chat_id).one()
        removed_accounts = []
        if not args:
            return self._help(bot, update)
        for arg in args:
            account = session.query(Account).filter_by(id=arg).one_or_none()
            account_subscribed = list(filter(lambda x: x.id == arg, chat.accounts))
            if account_subscribed:
                chat.accounts.remove(account)
                session.commit()
                removed_accounts.append(arg)
        session.close()
        bot.send_message(chat_id=chat_id, text="{} Account(s) removed!".format(len(removed_accounts)))

    def _deactivate_chat(self, bot, update):
        self._check_and_add_chat(update)
        session = Session()
        chat_id = update.message.chat_id
        chat = session.query(Chat).filter_by(id=chat_id).one()
        chat.subscription_active = False
        session.commit()
        bot.send_message(chat_id=chat_id, text="Chat deactivated. No more notifications!\n"
                                               "You can reactivate with /activate")

    def _activate_chat(self, bot, update):
        self._check_and_add_chat(update)
        session = Session()
        chat_id = update.message.chat_id
        chat = session.query(Chat).filter_by(id=chat_id).one()
        chat.subscription_active = True
        session.commit()
        bot.send_message(chat_id=chat_id, text="Chat activated!\n"
                                               "You can deactivate notifications with /deactivate")

    def _get_subscriptions(self, bot, update):
        self._check_and_add_chat(update)
        session = Session()
        chat_id = update.message.chat_id
        chat = session.query(Chat).options(eagerload(Chat.accounts)).filter_by(id=chat_id).one()
        message = "You have subscribed Account(s):\n"
        for account in chat.accounts:
            message += "`" + account.id + "`\n"
        if not chat.subscription_active:
            message += "NOTIFICATIONS DISABLED FOR THIS CHAT!"
        bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")

    @staticmethod
    def _check_and_add_chat(update):
        session = Session()
        chat_id = update.message.chat_id
        old_chat = session.query(Chat).filter_by(id=chat_id).one_or_none()
        if old_chat is None:
            session.add(Chat(id=chat_id))
            session.commit()
        session.close()

    @staticmethod
    def _help(bot, update):
        chat_id = update.message.chat_id
        help_text = "Usage:\n" \
                    "# subscribe notifications for wallets\n" \
                    "`/add`  <wallet1>  <wallet2>\n" \
                    "# remove subscriptions from wallets\n" \
                    "`/rm`  <wallet1>  <wallet2>\n" \
                    "# show your current subscriptions\n" \
                    "`/subscriptions`\n" \
                    "# activate notifications. Doesn't resend missed payments\n" \
                    "`/activate`\n" \
                    "# deactivate notifications from all subscribed addresses\n" \
                    "`/deactivate`\n" \
                    "# print help text\n" \
                    "`/help`\n" \
                    "# print informations about bot\n" \
                    "`/credits`"
        bot.send_message(chat_id=chat_id, text=help_text, parse_mode="Markdown")

    @staticmethod
    def _credits(bot, update):
        chat_id = update.message.chat_id
        credits_text = "Credits:\n" \
                       "Copyright © 2017 Tuomas Aho\n" \
                       "Follow this project on GitHub: https://github.com/tahv0/ethereumpaymentbot\n\n" \
                       "Donate: 0x744211bdd22f502cbA6A2265e981CB85384815cB\n" \
                       "Thanks!"
        bot.send_message(chat_id=chat_id, text=credits_text, parse_mode="Markdown")


