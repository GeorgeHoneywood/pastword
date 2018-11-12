from cryptography.fernet import Fernet

def createCipher():
    key = b'cnSl5YpL9PZbqFpSZ5VokHtGlEYlFgDe8NHdVM9N4Ig='
    cipher = Fernet(key)
    return cipher

def enc(decData):
    cipher = createCipher()
    encData = []

    for _, data in enumerate(decData): #not using item number
        #print(str(item) + ", " + str(data))
        
        data = str(data).encode()    #convert to bytes   
        encData.append(cipher.encrypt(data))    #encrypt

    encData.insert(0, None)
    print(encData)
        
    return tuple(encData) #convert to tuple and return it

def dec(encData):
    cipher = createCipher()
    decData = []

    for item, data in enumerate(decData):
        print(str(item) + ", " + str(data))
        data = str(data).decode()
        print(data)
        if item != 0:
            decData.append(cipher.decrypt(data))
        else:
            decData.append(data)
          
    print(decData)
        
    return tuple(decData) #convert to tuple and return it

