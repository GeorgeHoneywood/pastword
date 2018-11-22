import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from warningBox import warningBox

def createCipher(password):
    key = deriveKey(password)

    cipher = Fernet(key)
    return cipher

def deriveKey(password):
    salt = b'\xb9G)\xaf\xdb8\xc2\xe7\xfe\x9bw\xcbb\xe3\xe7U'
    bytesPass = password.encode()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    key = base64.urlsafe_b64encode(kdf.derive(bytesPass))

    return key

def enc(cipher, decLine):
    decLine = str(decLine).encode()
    return cipher.encrypt(decLine)

def dec(cipher, encLine):
    try:
        decLine = cipher.decrypt(encLine)
    except:
        warningBox("Please check your password", None)
        raise Exception("PasswordError")

    return decLine.decode()
