import hashlib
import json
import socket
import threading
from getKeys import generate_keys
import random

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

public_keys = {}
private_keys = {}
clients = []
txn_count = 0
message_buffer = []

blockChain = [
    "BLK/0000000000000000000000000000000000000000000000000000000000000000/TXN-Vivek-Kumar-300/TXN-Kumar-Vivek-100/TXN-Vivek-Vivek-100/0-Vivek-5/"
    + hashlib.sha256(
        "BLK/0000000000000000000000000000000000000000000000000000000000000000/TXN-Vivek-Kumar-100/TXN-Kumar-Vivek-100/TXN-Vivek-Vivek-100/0/".encode(
            "utf-8"
        )
    ).hexdigest()
]

accept = 0


plt.style.use("fivethirtyeight")
fig, ax = plt.subplots()

x_vals = []
y1_vals = []
y2_vals = []
y3_vals = []
y4_vals = []

alpha = 0.2  # For no, of clients
beta = 0.1  # No, of Transactions
gamma = 0.3  # No, of blocks
cost = 1


def update_cost(value):
    global cost
    cost = value
    return cost


changes = 0
prev = 0


def trans(txn, ch):
    n = txn - ch
    if n < 0:
        return 0
    return n


def animate(i):
    global changes
    global prev
    d = random.randint(1, 9)
    y = random.randint(5000, 10000)
    delta = (d / y) * (random.randint(random.randint(0, 2), random.randint(2, 3)))
    if txn_count != prev:
        prev = txn_count * i * 2
        changes = i
    x_vals.append(i)
    cost = update_cost(
        alpha * len(clients) + gamma * len(blockChain) + delta * i + beta * txn_count
    )
    y1_vals.append(cost)
    ax.clear()
    ax.plot(x_vals, y1_vals, label="Rate of Bitcoin Change", linewidth=0.5)
    ax.legend(loc="upper left")
    plt.tight_layout()


def show_plot():
    plt.tight_layout()
    plt.show()


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
        message_buffer[0] != message.split("/")[2]
        and message_buffer[1] != message.split("/")[3]
        and message_buffer[2] != message.split("/")[4]
    ):
        found_discrepancy = False
    if not found_discrepancy:
        if not found_dup:
            if found_prev:
                blockChain.append(message)
                message_buffer.clear()
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


def incr():
    txn_count = txn_count + 1


def handle_client(client_socket, clients):
    private_key, public_key = generate_keys()

    keys_data = {
        "public_key": public_key,
        "private_key": private_key,
    }
    client_socket.send(json.dumps(keys_data).encode())

    send_blockchain(client_socket)

    clients.append(client_socket)

    while True:
        try:
            data = client_socket.recv(8192)
            message = data.decode("utf-8")
            print(message)
            if message.startswith("BLK"):
                keep_block(message)
                broadcast_to_clients(message)
            elif message.startswith("TXN"):
                global txn_count
                global message_buffer
                txn_count = txn_count + 1
                message_buffer.append(message)
                broadcast_to_clients(message)
            elif message.startswith("RAT"):
                m = "VAL-" + str(update_cost(cost))
                client_socket.send(m.encode("utf-8"))
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
    # plot_thread = threading.Thread(target=show_plot)
    # plot_thread.start()

    # ani = FuncAnimation(fig, animate, interval=1000)
    # plt.show()
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    # Start the animation in the main thread
    ani = FuncAnimation(fig, animate, interval=1000)
    plt.show()
