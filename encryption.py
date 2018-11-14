import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from warningBox import warningBox

def createCipher():
    #password = input("Enter your password:\n")
    password = "dab password"
    key = deriveKey(password)
    print(key)

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

def enc(decData):
    cipher = createCipher()
    encData = []

    for item, data in enumerate(decData): #not using item number
        #print(str(item) + ", " + str(data))
        if item != 5:
            data = str(data).encode()    #convert to bytes
            encData.append(cipher.encrypt(data))    #encrypt
        else:
            encData.append(data)

    encData.insert(0, None)
        
    return tuple(encData) #convert to tuple and return it

def dec(encData):
    cipher = createCipher()
    decData = []
    rowList = []

    for _, rowData in enumerate(encData):
        for item, data in enumerate(rowData):
            #print(str(item) + ", " + str(data))
            if item != 0:
                try:
                    decBytes = cipher.decrypt(data)
                except:
                    warningBox("Please check your password", None)
                    raise Exception("PasswordError")
                rowList.append(decBytes.decode())
            else:
                rowList.append(data)

        decData.append(rowList)
        rowList = []
        
    return decData
