from cryptography.fernet import Fernet

def createCipher():
    key = b'cnSl5YpL9PZbqFpSZ5VokHtGlEYlFgDe8NHdVM9N4Ig='
    cipher = Fernet(key)
    return cipher

def enc(decData):
    cipher = createCipher()
    encData = []

    for item, data in enumerate(decData):
        print(str(item) + ", " + data)
        
        data = data.encode()    #convert to bytes   
        encData.append(cipher.encrypt(data))    #encrypt
        
    return tuple(encData) #convert to tuple and return it

def dec(encData):
    return decData

