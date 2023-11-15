import json
import socket
import threading
from transaction import Transaction
from getKeys import generate_keys


def private_send_keys_to_client(client_socket, public_key, private_key):
    private_key_data = json.dumps(
        {"n": private_key.n, "e": private_key.e, "d": private_key.d}
    )
    client_socket.send(f"PRIVATE_KEY:{private_key_data}".encode("utf-8"))


def public_send_keys_to_client(client_socket, public_key, private_key):
    public_key_data = json.dumps({"n": public_key.n, "e": public_key.e})
    client_socket.send(f"PUBLIC_KEY:{public_key_data}".encode("utf-8"))


def handle_client(client_socket, clients):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            for c in clients:
                c.send(data)
        except:
            break

    clients.remove(client_socket)
    client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(5)

    print("[*] Server listening on port 5555")

    clients = []

    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)

        # Send client their public and private key in the correct order
        public_key, private_key = generate_keys()

        client_handler = threading.Thread(
            target=handle_client, args=(client_socket, clients)
        )
        client_handler.start()


if __name__ == "__main__":
    start_server()
