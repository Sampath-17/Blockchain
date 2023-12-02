from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ed25519


def generate_keys():
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Serialize the keys to strings
    private_key_str = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    ).hex()

    public_key_str = public_key.public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    ).hex()

    return private_key_str, public_key_str


def verify_key_pair(private_key_str, public_key_str):
    try:
        # Deserialize keys from hex strings
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(
            bytes.fromhex(private_key_str)
        )
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(
            bytes.fromhex(public_key_str)
        )

        # Sign and verify a message to ensure key pair validity
        signature = private_key.sign(b"verification_test")

        public_key.verify(signature, b"verification_test")

        print("Key pair is valid.")
        return True
    except Exception as e:
        print(f"Key pair verification failed: {e}")
        return False
