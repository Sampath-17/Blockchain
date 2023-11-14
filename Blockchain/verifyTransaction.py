import rsa


def verify_transaction(sender, receiver, amount, time, signature, public_key):
    transaction = f"{sender} {receiver} {amount} {time}"

    decrypted_signature = rsa.decrypt(signature, public_key).decode("utf-8")

    if decrypted_signature == transaction:
        return True
    else:
        return False
