import json
import socket
import threading
import rsa
import random

from getKeys import verify_key_pair
from retrieve import load_blockchain, replace_blockchain

import hashlib

stage = False

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5555))

uname = ""


class Block:
    def __init__(self, data1, data2, data3, previous_hash, hash):
        self.data1 = data1
        self.data2 = data2
        self.data3 = data3
        self.previous_hash = previous_hash
        self.hash = hash


blockChain = [[]]

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
    nonce = random.randint(-100000, -1)
    if stage:
        nonce = random.randint(-1000000, -100001)
    print("Are you here?")
    abcd = blockChain[0][-1].split("/")[-1]
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
        print("Trying mining on value: ", nonce)
        if current_hash.startswith("0000") and nonce > 0:
            print("Obtained Nonce value: ", nonce)
            return current_hash, nonce
        nonce += 1


def check_buffer(messages, username):
    if stage:
        return
    if len(messages) == 3:
        current_hash, nonce = mining(messages)
        print("Created a block", messages, current_hash, nonce)
        data = (
            "BLK/"
            + blockChain[0][-1].split("/")[-1]
            + "/"
            + messages[0]
            + "/"
            + messages[1]
            + "/"
            + messages[2]
            + "/"
            + str(nonce)
            + "-"
            + username
            + "-"
            + "5"
            + "/"
            + current_hash
        )
        print("Trying to sent the block")
        client.send(data.encode("utf-8"))
        print("I sent the block to everyone")


def check_blockChain():
    return True


def find_chain(blocks, previous_hash="0" * 64):
    chain = []
    for block in blocks:
        if block.previous_hash == previous_hash:
            branch = find_chain(blocks, block.hash)
            if branch:
                block.branches = branch
            chain.append(block)
    return chain


def display_blocks(chain, indent=""):
    for block in chain:
        print(f"{indent}Data1: {block.data1}")
        print(f"{indent}Data2: {block.data2}")
        print(f"{indent}Data3: {block.data3}")
        print(f"{indent}Previous Hash: {block.previous_hash}")
        print(f"{indent}Hash: {block.hash}")

        if hasattr(block, "branches") and block.branches:
            print(f"{indent}Branches:")
            display_blocks(block.branches, indent + "  ")


def normalise():
    global stage
    global blockChain
    max_chain_length = max(len(chain) for chain in blockChain)
    blockChain = [chain for chain in blockChain if len(chain) >= max_chain_length - 1]
    if len(blockChain) > 1:
        stage = True
    else:
        stage = False
    print("Transaction stage: ", stage)


def add_block(message):
    previous_block_hash = message.split("/")[1]
    current_block_hash = message.split("/")[-1]
    k = -1
    duplicated = False
    for i, blocks in enumerate(blockChain):
        current_hash = blocks[-1].split("/")[-1]
        if current_hash == previous_block_hash:
            k = i
        if current_hash == current_block_hash:
            duplicated = True

    if duplicated:
        print("Block already taken!")
        return
    elif k != -1:
        blockChain[k].append(message)
        message_buffer.clear()
        normalise()
        return

    for i, blocks in enumerate(blockChain):
        for j, block in enumerate(blocks):
            current_hash = block.split("/")[-1]
            if current_hash == previous_block_hash:
                new_chain = blocks[: j + 1] + [message]
                blockChain.append(new_chain)
                message_buffer.clear()
                print(blockChain)
                normalise()
                return

    print("Block doesn't belong to your block chain")


def verify_transaction(obtained, transaction, signature):
    return signature == "digital"


def receive_messages(client_socket, username):
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
                    check_buffer(message_buffer, username)
                else:
                    print("Invalid Transaction! Hence Discarded.")
            elif received_data.startswith("BLK"):
                print("I think I received a block")
                add_block(received_data)
                if not stage:
                    replace_blockchain(blockChain)
            elif received_data.startswith("VAL"):
                print("Market Value of One Bitcoin is: ", received_data.split("-")[1])
            else:
                continue
        except:
            break


def check_amount(public_key):
    amounts = []
    for blocks in blockChain:
        amount = 0
        for block in blocks:
            t1 = block.split("/")[2]
            t2 = block.split("/")[3]
            t3 = block.split("/")[4]
            t4 = block.split("/")[5]
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
            if public_key == t4.split("-")[1]:
                amount = amount + int(t4.split("-")[2])
        amounts.append(amount)
    bf = 0
    for transaction in message_buffer:
        if public_key == transaction.split("-")[1]:
            bf = bf - int(transaction.split("-")[3])
        if public_key == transaction.split("-")[2]:
            bf = bf + int(transaction.split("-")[3])
    return (max(amounts) + bf), len(amounts)


def start_client():
    global uname
    global blockChain
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
    uname = username
    updated_blockchain_data = client.recv(8192).decode("utf-8")
    updated_blockchain = json.loads(updated_blockchain_data)
    blockChain[0] = updated_blockchain
    blockChain = load_blockchain()
    print("Initial Blockchain:", blockChain)

    receive_thread = threading.Thread(
        target=receive_messages,
        args=(
            client,
            username,
        ),
    )
    receive_thread.start()
    money, status = check_amount(username)
    if status > 1:
        print("You have a branching in your account!")
    print("You have this much amount: ", money)

    while True:
        message = input("Enter a message to send: ")
        if message.startswith("PBK"):
            print(blockChain)
        elif message.startswith("GET"):
            rname = message.split("-")[1]
            at, s = check_amount(rname)
            print(rname, " has ", at, " amount.")
        elif message.startswith("AMT"):
            mon, stat = check_amount(username)
            if stat > 1:
                print("You have a branching in your account!")
            print("You have this much amount: ", mon)
            money = mon
        elif message.startswith("TXN"):
            global stage
            if stage:
                print(
                    "Your block chain is in confusion stage, currently you can't transact"
                )
                continue
            # TXN-Receiver-Amount
            m = message.split("-")
            if len(m) != 3:
                print("Unappropriate Message format.")
            else:
                receiver = whos(m[1])
                amount = int(m[2])
                mon, stat = check_amount(username)
                money = mon
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
        elif message.startswith("TBF"):
            print(message_buffer)
        elif message.startswith("RAT"):
            client.send(message.encode("utf-8"))
        elif message.startswith("WBK"):
            wrong_block = (
                "BLK/<WeirdPreviousBlockHash>/TXN-Vivek-Kumar-300/TXN-Kumar-Vivek-100/TXN-Vivek-Vivek-100/0-Vivek-5/"
                + hashlib.sha256(
                    "BLK/<WeirdPreviousBlockHash>/TXN-Vivek-Kumar-300/TXN-Kumar-Vivek-100/TXN-Vivek-Vivek-100/0-Vivek-5/".encode(
                        "utf-8"
                    )
                ).hexdigest()
            )
            client.send(wrong_block.encode("utf-8"))
        elif message.startswith("TSG"):
            print("Transaction stage: ", stage)
        elif message.startswith("BCH"):
            t1 = "TXN-Vivek-" + username + "-500"
            t2 = "TXN-Vivek-" + username + "-600"
            t3 = "TXN-Vivek-" + username + "-700"
            c_hash, noncy = mining([t1, t2, t3])
            wrong_block = (
                "BLK/"
                + blockChain[0][-1].split("/")[-1]
                + "/"
                + t1
                + "/"
                + t2
                + "/"
                + t3
                + "/"
                + str(noncy)
                + "-"
                + username
                + "-5/"
                + c_hash
            )
            add_block(wrong_block)


if __name__ == "__main__":
    start_client()
