import datetime
from signTransaction import sign_transaction


class Transaction:
    def __init__(self, sender, recipient, amount, t, sign):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = t
        self.signature = sign

    def __str__(self):
        return f"Transaction({self.sender} => {self.amount} => {self.recipient} : {self.timestamp})"
