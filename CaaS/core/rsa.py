import os
from typing import Optional, Union, Literal, Tuple
from Crypto.PublicKey import RSA
from . import DefaultService
from CaaS.utils.algo import Algorithms



class RSAService(DefaultService):

    def __init__(
        self,
        byte_size: Optional[int] = 2048,
        format: Union[Literal["PEM"], Literal["DER"], Literal["OpenSSH"]] = "PEM",
        passphrase: Optional[str] = None
    ):
        super().__init__(Algorithms.rsa, os.getcwd())

        self.name = Algorithms.rsa
        self.byte_size = byte_size
        self.format = format
        self.passphrase = passphrase

        self.key = RSA.generate(self.byte_size)

    
    def update_paraphrase(self, paraphrase: str):
        self.passphrase = paraphrase

    
    def export_keys(self, passphrase: Optional[str] = None) -> Optional[Tuple[bytes, bytes]]:
        if not self.key:
            return None
        
        if passphrase and len(passphrase):
            self.update_paraphrase(passphrase)

        if self.passphrase and len(self.passphrase):
            private_key = self.key.export_key(format=self.format, protection=self.format, passphrase=self.passphrase)
        else:
            private_key = self.key.export_key(format=self.format, protection=self.format)    
        public_key = self.key.publickey().export_key(format=self.format)

        return (private_key, public_key)

    def generate_keys(self, file_name: str, passphrase: Optional[str] = None) -> Optional[bool]:
        if not file_name or not len(file_name):
            return None
        root = os.path.join(self.root, "temp")
        sk, pk = self.export_keys(passphrase=passphrase)
        self.write_file(
            file_name=file_name, 
            root=root, 
            write_mode="wb"
        ).write(sk)
        exists = self.is_file(file_name, root)
        self.write_file(
            file_name=file_name+".pub", 
            root=root, 
            write_mode="wb"
        ).write(pk)
        exists = exists and self.is_file(file_name+".pub", root)
        return exists
    

    