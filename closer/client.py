import json
import socket
import threading
import rsa
import random

from getKeys import verify_key_pair

import hashlib


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5555))


blockChain = []

message_buffer = []


def whos(username):
    try:
        with open("users.json", "r") as file:
            users = json.load(file)
            return users.get(username, None)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def adds(username, public_key):
    try:
        with open("users.json", "r") as file:
            users = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        users = {}
    available = True
    pk = public_key
    if username not in users:
        users[username] = public_key
        available = False
    pk = users[username]

    with open("users.json", "w") as file:
        json.dump(users, file, indent=4)

    print("Users on Network: ", users)
    return available, pk


def mining(messages):
    nonce = random.randint(-10000, -1)
    print("Are you here?")
    abcd = blockChain[-1].split("/")[-1]
    while True:
        n_temp = 0
        if nonce < 0:
            n_temp = (-1) * nonce
        else:
            n_temp = nonce
        data = (
            "BLK/"
            + abcd
            + "/"
            + messages[0]
            + "/"
            + messages[1]
            + "/"
            + messages[2]
            + "/"
            + str(n_temp)
            + "/"
        )
        current_hash = hashlib.sha256(data.encode("utf-8")).hexdigest()
        if current_hash.startswith("0000") and nonce > 0:
            return current_hash, nonce
        nonce += 1


def check_buffer(messages):
    if len(messages) == 3:
        current_hash, nonce = mining(messages)
        print("Created a block", messages, current_hash, nonce)
        data = (
            "BLK/"
            + blockChain[-1].split("/")[-1]
            + "/"
            + messages[0]
            + "/"
            + messages[1]
            + "/"
            + messages[2]
            + "/"
            + str(nonce)
            + "/"
            + current_hash
        )
        client.send(data.encode("utf-8"))
        print("I sent the block to everyone")
        messages.clear()


def check_blockChain():
    return True


def add_block(message):
    found_prev = False
    found_dup = False
    found_discrepancy = True
    previous_block_hash = message.split("/")[1]
    current_block_hash = message.split("/")[-1]
    for block in blockChain:
        current_hash = block.split("/")[-1]
        if current_hash == previous_block_hash:
            found_prev = True
        if current_hash == current_block_hash:
            found_dup = True
    if (
        message[0] != message.split("/")[2]
        and message[1] != message.split("/")[3]
        and message[2] != message.split("/")[4]
    ):
        found_discrepancy = False
    if not found_discrepancy:
        if not found_dup:
            if found_prev:
                blockChain.append(message)
                print(blockChain)
            else:
                print("Block doesn't belong to your block chain")
        else:
            print("Block already added to your block chain")
    else:
        print("Defected block received")


def verify_transaction(obtained, transaction, signature):
    return signature == "digital"


def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(8192)
            if not data:
                break

            received_data = data.decode("utf-8")
            if received_data.startswith("TXN"):
                sign = received_data.split("-")[-1]
                transaction = received_data.split(sign)[0]
                if verify_transaction(
                    whos(received_data.split("-")[1]), transaction, sign
                ):
                    print("Transaction is right!")
                    message_buffer.append(received_data)
                    print(received_data)
                    check_buffer(message_buffer)
                else:
                    print("Invalid Transaction! Hence Discarded.")
            elif received_data.startswith("BLK"):
                print("I think I received a block")
                add_block(received_data)
            else:
                continue
        except:
            break


def check_amount(public_key):
    amount = 0
    for block in blockChain:
        t1 = block.split("/")[2]
        t2 = block.split("/")[3]
        t3 = block.split("/")[4]
        if public_key == t1.split("-")[1]:
            amount = amount - int(t1.split("-")[3])
        if public_key == t1.split("-")[2]:
            amount = amount + int(t1.split("-")[3])
        if public_key == t2.split("-")[1]:
            amount = amount - int(t2.split("-")[3])
        if public_key == t2.split("-")[2]:
            amount = amount + int(t2.split("-")[3])
        if public_key == t3.split("-")[1]:
            amount = amount - int(t3.split("-")[3])
        if public_key == t3.split("-")[2]:
            amount = amount + int(t3.split("-")[3])
    return amount


def start_client():
    keys_json = client.recv(8192).decode("utf-8")
    keys_data = json.loads(keys_json)
    public_key = keys_data["public_key"]
    private_key = keys_data["private_key"]
    print("Your Keys are: ", private_key, public_key)
    username = input("Enter your UserName: ")
    available, pk = adds(username, str(public_key))
    if available:
        sk = input(
            "You seem to login for existing account, please provide you Private Key:"
        )
        verification_result = verify_key_pair(sk, pk)
        if verification_result:
            print("Private Key was yours, you can transact further")
            private_key = sk
            public_key = pk
        else:
            print("Private Key Verification Failed. Aborting...")
            return

    updated_blockchain_data = client.recv(8192).decode("utf-8")
    updated_blockchain = json.loads(updated_blockchain_data)
    blockChain.extend(updated_blockchain)
    print("Initial Blockchain:", blockChain)

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()
    money = check_amount(username)
    print("You have this much amount: ", money)

    while True:
        message = input("Enter a message to send: ")
        if message.startswith("PBK"):
            print(blockChain)
        elif message.startswith("AMT"):
            print("You have: ", money)
        elif message.startswith("TXN"):
            # TXN-Receiver-Amount
            m = message.split("-")
            if len(m) != 3:
                print("Unappropriate Message format.")
            else:
                receiver = whos(m[1])
                amount = int(m[2])
                if amount > money:
                    print(
                        "You don't have enough money for transacting this much amount"
                    )
                    print("You have: ", money)
                elif receiver != None:
                    message = "TXN-" + username + "-" + m[1] + "-" + m[2] + "-"
                    sign = "digital"
                    txn = message + sign
                    money = money - amount
                    client.send(txn.encode("utf-8"))
                else:
                    print("No such user found")


if __name__ == "__main__":
    start_client()
