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
            print(data)
            encData.append(cipher.encrypt(data))    #encrypt
        else:
            print("6")
            encData.append(data)

    encData.insert(0, None)
    tupEncData = tuple(encData)
        
    return tupEncData #convert to tuple and return it

def dec(encData):
    cipher = createCipher()
    decData = []

    for row, rowData in enumerate(encData):
        for item, data in enumerate(rowData):
            print(str(item) + ", " + str(data))
            if item != 0:
                decBytes = cipher.decrypt(data)
                decData.append(row[decBytes.decode()])
            else:
                decData.append(data)
            
    print(decData)
        
    return tuple(decData) #convert to tuple and return it

