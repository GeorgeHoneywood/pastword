import os
import getpass

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
backend = default_backend()

#not currently using salt for simplicity
#salt = os.urandom(16)

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

print("key - ", key)

message = str.encode("secret message")

padder = padding.PKCS7(128).padder()
padded_message = padder.update(message)
padded_message += padder.finalize()
print("padded data - ", padded_message)

iv = b'\x81\xd2\x17\x92K$\xc3\x0cI\n\xcf\xab\x99\xa2\x10\xbc'
cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
encryptor = cipher.encryptor()
ct = encryptor.update(padded_message) + encryptor.finalize()
decryptor = cipher.decryptor()
test = decryptor.update(ct) + decryptor.finalize() 
print("decypted data - ", test.decode("utf-8", "ignore"))
print("done")