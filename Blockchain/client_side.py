import socket
import threading
import rsa
import json
from getKeys import generate_keys
from transaction import Transaction
from signTransaction import sign_transaction
from datetime import datetime
import hashlib
from blockHash import calculate_hash

blockChain = [
    {
        "prevHash": "0000",
        "messages": ["K", "Vivek", "Kumar"],
        "currentHash": calculate_hash("0000", ["K", "Vivek", "Kumar"]),
    }
]

message_buffer = []


def mining(messages):
    nonce = 0
    while True:
        current_hash = calculate_hash(
            blockChain[-1]["currentHash"], messages + [str(nonce)]
        )
        if current_hash.startswith("0000"):
            return current_hash, nonce
        nonce += 1


def check_buffer(messages):
    if len(messages) == 3:
        messages = []
        current_hash, nonce = mining(messages)
        create_block(messages, current_hash, nonce)


def create_block(messages, current_hash, nonce):
    prev_hash = blockChain[-1]["currentHash"]
    new_block = {
        "prevHash": prev_hash,
        "messages": messages,
        "currentHash": current_hash,
        "nonce": nonce,
    }
    blockChain.append(new_block)
    print("New Block Created:", new_block)


def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            decrypted_message = data.decode("utf-8")
            message_buffer.append(decrypted_message)
            check_buffer(message_buffer)
            print(decrypted_message)
        except:
            break


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 5555))

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    while True:
        message = input("Enter a message to send: ")
        client.send(message.encode("utf-8"))


if __name__ == "__main__":
    start_client()
