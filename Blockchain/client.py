import socket
import threading
import rsa
import json
from getKeys import generate_keys
from transaction import Transaction
from signTransaction import sign_transaction
from datetime import datetime


def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            decrypted_message = data.decode("utf-8")
            print(decrypted_message)
        except:
            break


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 5555))

    # Initialize public and private keys
    public_key, private_key = generate_keys()

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    while True:
        receiver_public_key = input("Enter the public key of the other guy: ")
        amount = input("Enter the amount: ")

        # Call datetime.now() to get the current timestamp
        timestamp = datetime.now()

        to_send = Transaction(
            public_key,
            receiver_public_key,
            amount,
            timestamp,
            sign_transaction(
                public_key, receiver_public_key, amount, timestamp, private_key
            ),
        )

        client.send(str(to_send).encode("utf-8"))


if __name__ == "__main__":
    start_client()
