import hashlib
import json
import socket
import threading
from getKeys import generate_keys

public_keys = {}
private_keys = {}
clients = []

blockChain = [
    "BLK/0000000000000000000000000000000000000000000000000000000000000000/publickey/privatekey/amount/nonce/"
    + hashlib.sha256(
        "BLK/0000000000000000000000000000000000000000000000000000000000000000/publickey/privatekey/amount/nonce/".encode(
            "utf-8"
        )
    ).hexdigest()
]

accept = 0


def keep_block(message):
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


def broadcast_to_clients(message):
    for client in clients:
        client.send(message.encode("utf-8"))


def send_blockchain(client_socket):
    blockchain_data = json.dumps(blockChain)
    client_socket.send(blockchain_data.encode("utf-8"))


def handle_client(client_socket, clients):
    public_key, private_key = generate_keys()
    public_keys[client_socket] = public_key
    private_keys[client_socket] = private_key

    keys_data = {
        "public_key": {"n": public_key.n, "e": public_key.e},
        "private_key": {
            "n": private_key.n,
            "e": private_key.e,
            "d": private_key.d,
            "p": private_key.p,
            "q": private_key.q,
        },
    }
    client_socket.send(json.dumps(keys_data).encode())

    send_blockchain(client_socket)

    clients.append(client_socket)

    while True:
        try:
            data = client_socket.recv(1024)
            message = data.decode("utf-8")
            print(message)
            if message.startswith("BLK"):
                keep_block(message)
                broadcast_to_clients(message)
            elif message.startswith("TXN"):
                broadcast_to_clients(message)
            else:
                broadcast_to_clients(message)
        except:
            break

    clients.remove(client_socket)
    client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(5)

    print("[*] Server listening on port 5555")

    while True:
        client_socket, addr = server.accept()

        client_handler = threading.Thread(
            target=handle_client, args=(client_socket, clients)
        )
        client_handler.start()


if __name__ == "__main__":
    start_server()
