import json
import socket
import threading
import rsa

import hashlib


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5555))


blockChain = []

message_buffer = []


def mining(messages):
    nonce = 0
    print("Are you here?")
    abcd = blockChain[-1].split("/")[-1]
    while True:
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
            + str(nonce)
            + "/"
        )
        current_hash = hashlib.sha256(data.encode("utf-8")).hexdigest()
        if current_hash.startswith("0000"):
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


def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            received_data = data.decode("utf-8")
            if received_data.startswith("TXN"):
                message_buffer.append(received_data)
                print(received_data)
                check_buffer(message_buffer)
            elif received_data.startswith("BLK"):
                print("I think I received a block")
                add_block(received_data)
            else:
                continue
        except:
            break


def start_client():
    keys_json = client.recv(4096).decode("utf-8")
    keys_data = json.loads(keys_json)
    public_key = rsa.PublicKey(
        keys_data["public_key"]["n"], keys_data["public_key"]["e"]
    )
    private_key = rsa.PrivateKey(
        keys_data["private_key"]["n"],
        keys_data["private_key"]["e"],
        keys_data["private_key"]["d"],
        keys_data["private_key"]["p"],
        keys_data["private_key"]["q"],
    )
    print("Your Keys are: ", private_key, public_key)

    updated_blockchain_data = client.recv(4096).decode("utf-8")
    updated_blockchain = json.loads(updated_blockchain_data)
    blockChain.extend(updated_blockchain)
    print("Initial Blockchain:", blockChain)

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    while True:
        message = input("Enter a message to send: ")
        client.send(message.encode("utf-8"))


if __name__ == "__main__":
    start_client()
