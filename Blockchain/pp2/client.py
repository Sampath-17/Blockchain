import json
import socket
import threading
import rsa
from blockHash import calculate_hash
from classes import Transaction

import hashlib


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5555))


blockChain = ["BLK/0000/publickey/privatekey/amount/nonce/" + hashlib.sha256("BLK/0000/publickey/privatekey/amount/nonce/".encode("utf-8")).hexdigest()]

message_buffer = []

# def send_server(message):
#     client.send(message.encode("utf-8"))


def mining(messages):
    nonce = 0
    print("Are you here?")
    abcd = blockChain[-1].split("/")[-1]
    while True:
        data = "BLK/" + abcd + "/" + messages[0] + "/" + messages[1] + "/" + messages[2] + "/" + str(nonce) + "/"
        current_hash = hashlib.sha256(data.encode("utf-8")).hexdigest()
        if current_hash.startswith("0000"):
            return current_hash, nonce
        nonce += 1


def check_buffer(messages):
    if len(messages) == 3:
        current_hash, nonce = mining(messages)
        print("Created a block", messages, current_hash, nonce)
        data = "BLK/" + blockChain[-1].split("/")[-1] + "/" + messages[0] + "/" + messages[1] + "/" + messages[2] + "/" + str(nonce) + "/" + current_hash
        client.send(data.encode("utf-8"))
        messages.clear()


def create_block(messages, current_hash, nonce):
    pass


block_buffer = []


def check_blockChain():
    return True


def add_block(message):
    block_buffer.append(message)
    print("I added to the buffer")
    if check_blockChain():
        print("I think its right for this blockChain")
        client.send("CHK/T".encode("utf-8"))


def update_recent(message):
    # Check the truth of adding the block in block Chain or not
    print("Should be done")


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
            elif received_data.startswith("UPT"):
                update_recent(received_data)
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
