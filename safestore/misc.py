from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

file = "configuration/private_srds.pem"
with open(file, "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
    )
