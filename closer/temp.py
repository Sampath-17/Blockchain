import json
import socket
import threading
import rsa
import random

from getKeys import verify_key_pair

import hashlib


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
    nonce = random.randint(-10000, -1)
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
        if current_hash.startswith("00") and nonce > 0:
            print("Obtained Nonce value: ", nonce)
            return current_hash, nonce
        nonce += 1


def check_buffer(messages, username):
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
        messages.clear()


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


def add_block(message):
    found_prev = -1
    found_dup = False
    found_discrepancy = True
    previous_block_hash = message.split("/")[1]
    current_block_hash = message.split("/")[-1]
    branch = False
    branchAt = -1
    branchIn = -1
    i = 0
    k = 0
    for blocks in blockChain:
        j = 0
        for block in blocks:
            current_hash = blocks[j].split("/")[-1]
            if current_hash == current_block_hash:
                branchAt = j
                found_dup = True
            j = j + 1
        if branchAt != len(blocks) - 1:
            branch = True
            branchIn = k
        k = k + 1
    if branch:
        temp_block_chain = blockChain[branchIn][:branchAt]
        temp_block_chain.append(message)
        blockChain.append(temp_block_chain)
    else:
        for block in blockChain:
            current_hash = block[-1].split("/")[-1]
            if current_hash == previous_block_hash:
                found_prev = i
            i = i + 1
        if (
            len(message) == 3
            and message[0] != message.split("/")[2]
            and message[1] != message.split("/")[3]
            and message[2] != message.split("/")[4]
        ):
            found_discrepancy = False
        if len(message) < 3:
            found_discrepancy = False
        if not found_discrepancy:
            if not found_dup:
                if found_prev != -1:
                    blockChain[found_prev].append(message)
                    print(blockChain)
                else:
                    print("Block doesn't belong to your block chain")
            else:
                print("Block already added to your block chain")
        else:
            print("Defected block received")


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
    return max(amounts), len(amounts)


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
    uname = username
    updated_blockchain_data = client.recv(8192).decode("utf-8")
    updated_blockchain = json.loads(updated_blockchain_data)
    blockChain[0] = updated_blockchain
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
