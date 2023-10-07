import os, math
from typing import Optional, TypedDict
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from . import DefaultService
from CaaS.utils.algo import Algorithms


class EncryptionData(TypedDict):
    token: str
    ct: str
    tag: str
    nonce: str

class AESService(DefaultService):

    def __init__(self, nonce: Optional[str] = None, token : Optional[str] = None):
        super().__init__(Algorithms.aes, os.getcwd())
        
        self.name = Algorithms.aes
        self.root = os.getcwd()
        self.byte_size = 32
        self.generated_str_size = math.ceil(self.byte_size*8/6)+1
        self.cipher = None
        self.token = None
        
        if nonce and token:
            self.create_token(self.get_bytes(nonce), token)
        elif nonce:
            self.create_token(self.get_bytes(nonce))
        elif token:
            self.create_token(token=token)
        else:
            self.create_token()

        
    def create_token(self, nonce: Optional[bytes] = None, token: Optional[str] = None):
        if not token:
            self.secret_key = get_random_bytes(self.byte_size)
            self.token = self.get_base64(self.secret_key)
        else:
            self.token = token
            self.secret_key = self.get_bytes(token)
        if nonce:
            self.cipher = AES.new(self.secret_key, mode=AES.MODE_EAX, nonce=nonce)
        else:
            self.cipher = AES.new(self.secret_key, mode=AES.MODE_EAX)
        


    def get_nonce(self):
        if not self.cipher:
            return None
        return self.get_base64(self.cipher.nonce)


    def encrypt(self, data: str) -> EncryptionData:
        if not self.cipher:
            return None
        cipher_text, tag =  self.cipher.encrypt_and_digest(bytes(data, self.encoding))
        return EncryptionData(
            ct=self.get_base64(cipher_text),
            tag=self.get_base64(tag),
            nonce=self.get_nonce(),
            token=self.token
        )


    def _verify(self, tag: str, nonce: Optional[str] = None):
        if nonce:
            self.create_token(self.get_bytes(nonce))
        
        if not self.cipher:
            return None
        return self.cipher.verify(self.get_bytes(tag))
    

    def decrypt(self, ed: EncryptionData) -> Optional[str]:
        pt = self.cipher.decrypt(self.get_bytes(ed["ct"]))
        return pt.decode(self.encoding)
    
    def decrypt_ct(self, ct: str) -> Optional[str]:
        pt = self.cipher.decrypt(self.get_bytes(ct))
        return pt.decode(self.encoding)
    


        

        
        

        
