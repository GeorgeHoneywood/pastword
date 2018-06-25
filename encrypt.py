import os
import getpass

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
backend = default_backend()

#not currently using salt for simplicity
salt = os.urandom(16)

#generate key using scrypt kdf
kdf = Scrypt(
    salt = b'\x9d\x97#\xbc\xc4B\xdd\xb7\x9c\xff8\x9e\xab\xa6&\x07',
    length = 32,
    n = 2**18,
    r = 8,
    p = 1,
    backend = backend
)

password = getpass.getpass("Enter password:\n")

key = kdf.derive(str.encode(password))

print(key)