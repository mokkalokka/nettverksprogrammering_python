# dependency sqlalchemy
# pip install sqlalchemy for installation

import socket
import threading
import time
import datetime
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQL Alchemy setup
Base = declarative_base()
engine = create_engine('sqlite:///db.sqlite3')


# ORM model
class Account(Base):
    __tablename__ = "account"
    account_nr = Column(Integer, primary_key=True)
    name = Column(String)
    balance = Column(Float)
    last_updated = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now)


session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)

# Socket setup:
PORT = 3030
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), PORT))
s.listen(5)
print(f"Server is running, listening on port {PORT}")


def clients():
    while True:
        # now our endpoint knows about the OTHER endpoint.
        clientsocket, address = s.accept()
        print(f"Connection from {address} has been established.")
        clientsocket.send(bytes(welcome, "utf-8"))
        while True:
            try:
                data = clientsocket.recv(2048)
                dataStr = data.decode("utf-8")

                if not data:
                    break

                print("Client Says: " + dataStr)
                commands = dataStr.split(" ", 100)

                msg = "Invalid syntax! Type help for commands"

                if commands[0] == "create":
                    msg = create(commands[1], commands[2])
                elif commands[0] == "withdraw" and len(commands) == 5:
                    if commands[3] == "safe":
                        msg = withdraw(commands[1], commands[2], commands[4])
                    elif commands[3] == "unsafe":
                        msg = unsafe_withdraw(commands[1], commands[2], commands[4])
                elif commands[0] == "withdraw":
                    msg = withdraw(commands[1], commands[2], 0)
                elif commands[0] == "deposit":
                    msg = deposit(commands[1], commands[2])
                elif commands[0] == "edit":
                    msg = edit(commands[1], commands[2])
                elif commands[0] == "accounts" and len(commands) == 3:
                    msg = accounts_by_balance(commands[2])
                elif commands[0] == "accounts":
                    msg = accounts()
                elif commands[0] == "help":
                    msg = help

                clientsocket.sendall(bytes(msg, "utf-8"))

            except socket.error:
                print("Error Occured.")
                break


def create(name, balance):
    session_instant = session()
    account = Account(name=name, balance=balance)
    session_instant.add(account)
    session_instant.commit()
    return f'Created account, account number: {account.account_nr}'


def withdraw(amount, name, seconds):
    session_instant = session()
    while True:

        tmp_account_balance = session_instant.query(Account).filter(Account.name == name).first().balance
        tmp_account_balance -= float(amount)
        tmp_account_last_updated = session_instant.query(Account).filter(Account.name == name).first().last_updated

        # sleep
        time.sleep(float(seconds))

        if tmp_account_balance >= 0:
            account = session_instant.query(Account).filter(Account.name == name).first()

            #Optimistic lock
            if tmp_account_last_updated == account.last_updated:
                account.balance = tmp_account_balance
                session_instant.commit()
                data = f'Withdrew {amount} from account nr: {account.account_nr}. Remaining balance is: {account.balance}'
                break
            else:
                print("wrong timestamp, trying again")
        else:
            data = "Insufficient funds"
            break
    return data


def unsafe_withdraw(amount, name, seconds):
    session_instant = session()

    account_balance = session_instant.query(Account).filter(Account.name == name).first().balance

    # sleep for 10 seconds, to invoke transaction error
    time.sleep(float(seconds))

    account = session_instant.query(Account).filter(Account.name == name).first()

    if account_balance >= float(amount):
        account.balance = account_balance - float(account_balance)

        #No lock = unsafe
        session_instant.commit()
        return f'Withdrew {amount} from account nr: {account.account_nr}. Remaining balance is: {account.balance}'
    else:
        return "Insufficient funds"


def deposit(amount, name):
    session_instant = session()
    account = session_instant.query(Account).filter(Account.name == name).first()
    account.balance += float(amount)
    session_instant.commit()
    return f'Deposited {amount} to account nr: {account.account_nr}. New balance is: {account.balance}'


def accounts():
    session_instant = session()
    accounts = session_instant.query(Account).all()
    data = "Accounts in the database:\n\naccount_nr:\tname:\t\tbalance:\t\tlast_updated:\n"

    for account in accounts:
        data += f'{account.account_nr}\t\t{account.name}\t\t{account.balance}\t\t{account.last_updated}\n'
    return data


def accounts_by_balance(balance):
    session_instant = session()
    accounts = session_instant.query(Account).filter(Account.balance > balance)
    data = f"Accounts in the database with balance greater than {balance}:\n\naccount_nr:\tname:\t\tbalance:\t\tlast_updated\n"

    for account in accounts:
        data += f'{account.account_nr}\t\t{account.name}\t\t{account.balance}\t\t{account.last_updated}\n'
    return data


def edit(name, new_name):
    session_instant = session()
    account = session_instant.query(Account).filter(Account.name == name).first()
    account.name = new_name
    session_instant.commit()
    return f'Account nr: {account.account_nr} has changed name to {new_name}'


threads = []
for i in range(5):
    threads.append(threading.Thread(target=clients))
    threads[i].start()

# Messages
help = "Commands\n" \
       "Create account: create [name] [initial balance]\n" \
       "Withdraw money: withdraw [amount] [from name], optional [safe|unsafe] [seconds]. Sleeps before editing safe or unsafe transaction\n" \
       "Deposit money: deposit [amount] [to name]\n" \
       "Edit name: edit [old_name] [new_name]\n" \
       "Show accounts: accounts\n" \
       "Show accounts with balance greater than x: accounts -gt [x]\n" \
       "Show commands: help"

welcome = "Welcome to the bank cli\n" + help
