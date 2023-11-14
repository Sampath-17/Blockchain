import rsa


def generate_keys():
    public_key, private_key = rsa.newkeys(2048)

    return public_key, private_key
