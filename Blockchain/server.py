import socket
import threading


def handle_client(client_socket, clients):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            # Broadcast the message to all clients
            for c in clients:
                if c != client_socket:
                    c.send(data)
        except:
            break

    # Remove the client from the list if disconnected
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

        client_handler = threading.Thread(
            target=handle_client, args=(client_socket, clients)
        )
        client_handler.start()


if __name__ == "__main__":
    start_server()
