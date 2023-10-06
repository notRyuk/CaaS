import os
from typing import Optional
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from base64 import b64decode, b64encode
from . import DefaultService
from CaaS.utils.algo import Algorithms


class AESService(DefaultService):

    def __init__(self, byte_size: Optional[int] = 2048):
        super().__init__(Algorithms.aes, os.getcwd())
        
        self.name = Algorithms.aes
        self.root = os.getcwd()
        self.byte_size = byte_size
        self.aes_byte_size = 32
        self.cipher = AES.new(get_random_bytes(self.aes_byte_size), AES.MODE_EAX)
    
    def create_secret_key(self, secret_text: Optional[str] = None) -> bytes:
        if not secret_text or not len(secret_text):
            secret_text = get_random_bytes(self.byte_size)
            secret_text = b64encode(secret_text).decode(self.encoding)
        else:
            if len(secret_text) > self.byte_size:
                secret_text = secret_text[:self.byte_size]
            secret_text = bytes(secret_text, self.encoding)
            secret_text = b64encode(secret_text).decode(self.encoding)
            random_text = get_random_bytes(self.byte_size-len(secret_text)-1)
        
        return secret_text