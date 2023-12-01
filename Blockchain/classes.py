import hashlib


class Transaction:
    def __init__(self, sender, recipient, amount, t, sign):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = t
        self.signature = sign

    def __str__(self):
        return f"TN/{self.sender}/{self.recipient}/{self.amount}/{self.timestamp}/{self.signature}"


class Block:
    def __init__(self, prevHash, arr, nonce):
        self.prevHash = prevHash
        self.arr = arr
        self.nonce = nonce
        self.currentHash = self.calculate_hash()
        self.nextBlock = None

    def __str__(self):
        return f"BK/{self.prevHash}/{self.arr}/{self.nonce}/{self.currentHash}"

    def calculate_hash(self):
        return hashlib.sha256(str(self).encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.head = None
        self.branches = []
