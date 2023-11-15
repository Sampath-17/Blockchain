import hashlib


def calculate_hash(prev_hash, messages):
    data = prev_hash + "".join(messages)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()
