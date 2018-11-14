from cryptography.fernet import Fernet

def createCipher():
    key = b'cnSl5YpL9PZbqFpSZ5VokHtGlEYlFgDe8NHdVM9N4Ig='
    cipher = Fernet(key)
    return cipher

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
                decBytes = cipher.decrypt(data)
                rowList.append(decBytes.decode())
            else:
                rowList.append(data)

        decData.append(rowList)
        rowList = []
        
    return decData
