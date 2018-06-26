import os
import getpass

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
backend = default_backend()

#not currently using salt for simplicity
#salt = os.urandom(16)

password = getpass.getpass("Enter password - ")

def generate_key(password):
    #generate key using scrypt kdf
    kdf = Scrypt(
    salt = b'\x9d\x97#\xbc\xc4B\xdd\xb7\x9c\xff8\x9e\xab\xa6&\x07',
    length = 32,
    n = 2**18,
    r = 8,
    p = 1,
    backend = backend
    )

    key = kdf.derive(str.encode(password))

    #print("key - ", key)

    return key

def padder():
    message = str.encode(input("Enter data to encrypt - "))

    padder = padding.PKCS7(128).padder()
    padded_message = padder.update(message)
    padded_message += padder.finalize()

    #print("padded message - ", padded_message)

    return padded_message

def generate_cipher(key):
    iv = b'\x81\xd2\x17\x92K$\xc3\x0cI\n\xcf\xab\x99\xa2\x10\xbc'
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    return cipher


def encrypt(key, cipher, padded_message):
    encryptor = cipher.encryptor()
    padded_encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
    return (padded_encrypted_message, cipher)

def decrypt(padded_encrypted_message, cipher):
    decryptor = cipher.decryptor()
    padded_decrypted_message = decryptor.update(padded_encrypted_message) + decryptor.finalize()

    #print("padded_decrypted_message", padded_decrypted_message)

    return padded_decrypted_message
    
def depadder(padded_decrypted_message):
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_message = unpadder.update(padded_decrypted_message)
    decrypted_message += unpadder.finalize()

    #print("decrypted_message", decrypted_message)

    return decrypted_message

def main():
    choice = input("Please pick an option:\n1. Encrypt\n2. Decrypt\n...  ")

    if choice == "1":
        file = open("data.txt", "w")

        key = generate_key(password)
        padded_message = padder()
        cipher = generate_cipher(key)
        padded_encrypted_message, cipher = encrypt(key, cipher, padded_message)

        file.write(padded_encrypted_message.decode("utf-8", "ignore") + "\n")
        print(type(cipher))
        file.write(str(cipher))

    elif choice == "2":
        file = open("data.txt", "r")

        padded_encrypted_message = str.encode(file.readline(0))
        cipher = file.readline(1)
        cipher = cipher.__class__ = Cipher

        padded_decrypted_message = decrypt(padded_encrypted_message, cipher)
        decrypted_message = depadder(padded_decrypted_message)

        print("decrypted data - ", decrypted_message.decode("utf-8", "ignore"))

    else:
        print("Invalid input")
        exit()
    
    file.close()

main()