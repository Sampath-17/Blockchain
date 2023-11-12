# import subprocess
# import os

# # Create a new process group for the child process
# os.setsid()

# # Create the child process
# process = subprocess.Popen(
#     ['python', 'other_script.py'],
#     shell=False
# )

# # Capture the child process's output
# stdout, stderr = process.communicate()
# print(stdout)
import hashlib
import time

def generate_proof_of_work(difficulty):
    i = 0
    while True:
        nonce = 1
        timestamp = i
        data = "This is a proof of work example. nonce: " + str(nonce) + ", timestamp: " + str(timestamp)
        data = data.encode("utf-8")
        hash_object = hashlib.sha256(data)
        hex_digest = hash_object.hexdigest()

        if hex_digest.startswith('0' * difficulty):
            return hex_digest, nonce, timestamp
        i = i + 1

difficulty = 5  # Adjust the difficulty level here
print("flag")

proof_of_work, nonce, timestamp = generate_proof_of_work(difficulty)

print(f"Proof of work: {proof_of_work}")
print(f"Nonce: {nonce}")
print(f"Timestamp: {timestamp}")
