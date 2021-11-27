import hashlib

SHARED_KEY = b'meshd'


def hash_payload(payload):
    """
    Calculate the hash of the payload using the shared key.
    """
    m = hashlib.sha256()
    m.update(payload + SHARED_KEY)
    return m.digest()
