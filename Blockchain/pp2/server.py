import json
import socket
import threading
from transaction import Transaction
from getKeys import generate_keys
from blockHash import calculate_hash

public_keys = {}
private_keys = {}
clients = []

blockChain = []



def broadcast_to_clients(message):
    for client in clients:
        client.send(message.encode("utf-8"))


accept = 0

def check_acceptance():
    if accept >= 1:
        broadcast_to_clients("UPT/T")
    else:
        broadcast_to_clients("UPT/F")


def statistics(message):
    print("Came here")
    print(message.endswith("T"))
    if message.endswith("T") == True:
        accept = accept + 1
        print(accept)
        check_acceptance()
    else:
        return



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
            if message.startswith("CHK"):
                statistics(message)
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
