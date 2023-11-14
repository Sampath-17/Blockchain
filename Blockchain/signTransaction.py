import rsa


def sign_transaction(sender, receiver, amount, time, private_key):
    transaction = f"{sender} {receiver} {amount} {time}"

    signature = rsa.encrypt(transaction.encode("utf-8"), private_key)

    return signature
