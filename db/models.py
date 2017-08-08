#!/usr/bin/env python
from sqlalchemy import Column, UniqueConstraint, DateTime, String, func, Boolean, Integer, BigInteger, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from config_parser.config_parser import get_config_value
Base = declarative_base()

subscription_table = Table('subscription', Base.metadata,
                           Column('chat_id',
                                  BigInteger,
                                  ForeignKey('chat.id')),
                           Column('account_id',
                                  String(convert_unicode=True,length=255),
                                  ForeignKey('account.id')),
                           UniqueConstraint('chat_id', 'account_id')
                           )


class Chat(Base):
    __tablename__ = 'chat'
    id = Column(BigInteger, primary_key=True, autoincrement=False, nullable=False)
    subscription_active = Column(Boolean, default=True, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    accounts = relationship('Account', secondary=subscription_table,
                            back_populates='chats')


class Account(Base):
     __tablename__ = 'account'
     # something like 42 chars should be long enough, but lol
     id = Column(String(convert_unicode=True, length=255), primary_key=True, nullable=False)
     # no updated_at column because it never gets updated
     created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
     chats = relationship('Chat', secondary=subscription_table,
                          back_populates='accounts')
     accountbalances = relationship('AccountBalance', cascade='all, delete-orphan')


class AccountBalance(Base):
     __tablename__ = 'accountbalance'
     # no need for id or primary key, but lets add anyway
     id = Column(Integer, autoincrement=True, primary_key=True)
     account_id = Column(String(convert_unicode=True, length=255), ForeignKey('account.id'),  nullable=False)
     # balance is in wei
     balance = Column(BigInteger, primary_key=False, autoincrement=False, nullable=False)
     # no updated_at column because new row is inserted when account balance changes
     # change_in_money: eg. { 'EUR': 200.30, 'USD': 230.44 }
     change_in_money = Column(JSON, nullable=False)
     created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)


from sqlalchemy import create_engine


def get_db_url():
    # dialect+driver://username:password@host:port/database
    dialect_driver = get_config_value("DATABASE", "dialect+driver")
    uname = get_config_value("DATABASE", "username")
    password = get_config_value("DATABASE", "password")
    host = get_config_value("DATABASE", "host")
    port = get_config_value("DATABASE", "port")
    database = get_config_value("DATABASE", "database")
    return "{}://{}:{}@{}:{}/{}".format(
        dialect_driver,
        uname,
        password,
        host,
        port,
        database)

engine = create_engine(get_db_url())

from sqlalchemy.orm import sessionmaker
Session = sessionmaker()
Session.configure(bind=engine)
Base.metadata.create_all(engine)