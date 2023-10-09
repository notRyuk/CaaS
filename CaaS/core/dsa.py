import os
from typing import Optional, Union, Literal, Tuple
from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

from CaaS.models.otp import Otp

from . import DefaultService
from CaaS.utils.algo import Algorithms

class DSAService(DefaultService):

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
        self.key = None

    
    def update_paraphrase(self, paraphrase: str):
        self.passphrase = paraphrase

    
    def export_keys(self, passphrase: Optional[str] = None) -> Optional[Tuple[bytes, bytes]]:
        if not self.key:
            return None
        
        if passphrase and len(passphrase):
            self.update_paraphrase(passphrase)

        if self.passphrase and len(self.passphrase):
            private_key = self.key.export_key(passphrase=self.passphrase)
        else:
            private_key = self.key.export_key()
        public_key = self.key.publickey().export_key()

        return (private_key, public_key)

    def generate_keys(self,userId: str, passphrase: Optional[str] = None) -> Optional[bool]:
        if not userId:
            return None
        if not os.path.isdir(os.path.join(self.root, "temp", userId)):
            os.mkdir(os.path.join(self.root, "temp", userId))
        file_name = "id_dsa"
        root = os.path.join(self.root, "temp", userId)
        self.key = DSA.generate(self.byte_size)
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
        return exists and self.is_file(file_name+".pub", root)
    
    def encrypting(self, email: str, id: str, otp: int): # take user id input
        if not os.path.isfile(os.path.join(self.root, "temp", id, "id_dsa")):
            return None
        hash_obj = SHA256.new(bytes(f"{email}:{otp}", self.encoding))
        print(self.get_base64(hash_obj.digest()))
        self.key = DSA.import_key(
            self.read_file(os.path.join(self.root, "temp", id, "id_dsa")).read(),
            passphrase=email
        )
        signer = DSS.new(self.key, 'fips-186-3')
        signature = signer.sign(hash_obj)
        return self.get_base64(signature)
    
    def decrypting(self, email: str, id: str, otp: int, signature: str):
        if not os.path.isfile(os.path.join(self.root, "temp", id, "id_dsa.pub")):
            return None
        hash_obj = SHA256.new(bytes(f"{email}:{otp}", self.encoding))
        self.key = DSA.import_key(self.read_file(os.path.join(self.root, "temp", id, "id_dsa.pub")).read())
        verifier = DSS.new(self.key, 'fips-186-3')
        try:
            verifier.verify(hash_obj, self.get_bytes(signature))
            return True
        except ValueError:
            return False




    

    