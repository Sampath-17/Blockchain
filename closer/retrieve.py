import json


def load_blockchain(filename="blockchain.json"):
    try:
        with open(filename, "r") as file:
            blockchain_data = json.load(file)
        return blockchain_data
    except FileNotFoundError:
        return []


def replace_blockchain(new_blockchain, filename="blockchain.json"):
    try:
        with open(filename, "w") as file:
            json.dump(new_blockchain, file)
        print("Blockchain replaced successfully.")
    except Exception as e:
        print(f"Error replacing blockchain: {e}")
