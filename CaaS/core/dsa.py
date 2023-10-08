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
        self.key = DSA.generate(self.byte_size)

    
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

    def generate_keys(self,userId: str,passphrase: Optional[str] = None) -> Optional[bool]:
        if not userId:
            return None
        if not os.path.isdir(os.path.join(self.root, "temp", userId)):
            os.mkdir(os.path.join(self.root, "temp", userId))
        file_name="id_dsa"
        root = os.path.join(self.root, "temp", userId)
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
    
    def encrypting(self, email, id, otp): # take user id input
        if not os.path.isfile(os.path.join(self.root, "temp", id, "id_dsa")):
            pass
        hash_obj = SHA256.new(f"{email}:{otp}")
        self.key = DSA.import_key(os.path.join(self.root, "temp", id, "id_dsa")) # private key file
        
        signer = DSS.new(self.key, 'fips-186-3')
        signature = signer.sign(hash_obj)
        ootp=Otp(email=email,signature=signature)
        ootp.insert()
        return self.get_base64(signature)
    
    def decrypting(self,email,id,otp):
        hash_obj = SHA256.new(f"{email}:{otp}")
        self.key = DSA.import_key(os.path.join(self.root, "temp", id, "id_dsa.pub"))
        # public key file
        verifier = DSS.new(self.key, 'fips-186-3')
        ootp=Otp.find_one({"email":email})
        try:
            verifier.verify(hash_obj, ootp.signature)
            print("The message is authentic.")
        except ValueError:
            print("The message is not authentic.")
        




    

    