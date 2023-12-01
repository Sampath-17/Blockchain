import json
import socket
import threading
import rsa
from blockHash import calculate_hash
from classes import Transaction

import hashlib



blockChain = ["BLK/0000/publickey/privatekey/amount/nonce/" + hashlib.sha256("BLK/0000/publickey/privatekey/amount/nonce/".encode("utf-8")).hexdigest()]

message_buffer = []

def send_server(client, message):
    client.send(message.encode("utf-8"))


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
        send_server(client,data)
        message_buffer.clear()


def create_block(messages, current_hash, nonce):
    prev_hash = blockChain[-1]["currentHash"]
    
    blockChain.append(new_block)


block_buffer = blockChain[0]


def check_blockChain():
    return True


def add_block(message):
    block_buffer = message
    print("Added to block buffer")
    if check_blockChain():
        send_server(client,"CHK/T")
    else:
        send_server(client,"CHK/F")


def update_recent(message):
    # Check the truth of adding the block in block Chain or not
    if message.endswith("T"):
        print("Appended to the block chain")
        blockChain.append(block_buffer)


def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            received_data = data.decode("utf-8")
            print(received_data)
            if received_data.startswith("TXN"):
                message_buffer.append(received_data)
                print(received_data)
                check_buffer(message_buffer)
            elif received_data.startswith("BLK"):
                add_block(received_data)
            elif received_data.startswith("UPT"):
                update_recent(received_data)
            else:
                continue
        except:
            break


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 5555))
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
        send_server(client, message)


if __name__ == "__main__":
    start_client()
