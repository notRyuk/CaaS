import os
from typing import Literal, Optional, Tuple, Union

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

from CaaS.utils.algo import Algorithms

from . import DefaultService
from .aes import EncryptionData as ED


class EncryptionData(ED):
    key_type: Union[Literal["pk"], Literal["sk"]]
    secret_token: str

class RSAService(DefaultService):

    def __init__(
        self,
        byte_size: Optional[int] = 2048,
        format: Union[Literal["PEM"], Literal["DER"], Literal["OpenSSH"]] = "PEM",
        passphrase: Optional[str] = None
    ):
        super().__init__(Algorithms.rsa)

        self.name = Algorithms.rsa
        self.byte_size = byte_size
        self.format = format
        self.passphrase = passphrase
        self.secret_key = None
        self.token = None

        self.key = RSA.generate(self.byte_size)
        self.cipher = PKCS1_OAEP.new(self.key)
        self.session_cipher = None

    
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

    def generate_keys(self, file_name: str, dir_name: Optional[str] = None, passphrase: Optional[str] = None) -> Optional[bool]:
        if not file_name or not len(file_name):
            return None
        if not os.path.isdir(os.path.join(self.root, dir_name)):
            os.mkdir(os.path.join(self.root, dir_name))
        root = os.path.join(self.root, dir_name) if dir_name and len(dir_name) else self.root
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
    

    def create_token(self, file_name: str, root: Optional[str] = None, passphrase: Optional[str] = None):
        if not file_name or not len(file_name):
            return None
        if passphrase and len(passphrase):
            self.key = RSA.import_key(self.read_file(file_name, "r", self.root if not root else root).read(), passphrase=passphrase)
        else:    
            self.key = RSA.import_key(self.read_file(file_name, "r", self.root if not root else root).read())
        self.secret_key = get_random_bytes(32) # session key
        self.token = self.get_base64(self.secret_key)
        self.cipher = PKCS1_OAEP.new(self.key)
        self.encrypted_secret_key = self.cipher.encrypt(self.secret_key)
        self.session_cipher = AES.new(self.secret_key, AES.MODE_EAX)
    
    def encrypt(
        self, 
        data: str,
        file_name: str,
        key_type: Union[Literal["pk"], Literal["sk"]] = "sk",
        passphrase: Optional[str] = None,
        root: Optional[str] = None
    ) -> Optional[EncryptionData]:
        if not file_name or not data:
            return None
        self.create_token(file_name, root, passphrase)
        ct, tag = self.session_cipher.encrypt_and_digest(data)
        return EncryptionData( 
            ct=self.get_base64(ct),
            tag=self.get_base64(tag),
            nonce=self.get_base64(self.session_cipher.nonce),
            key_type=key_type,
            secret_token=self.get_base64(self.encrypted_secret_key)
        )
    
    def decrypt(
        self, 
        ed: EncryptionData, 
        file_name: str, 
        passphrase: Optional[str] = None, 
        root: Optional[str] = None
    ) -> Optional[str]:
        if not ed or not file_name or not len(file_name):
            return None
        if ed["key_type"] == "sk" and not file_name.endswith(".pub"):
            return "Private key is used for encrypting a public key is not provided"
        elif ed["key_type"] == "pk" and file_name.endswith(".pub"):
            return "Public key is used for encrypting a private key is not provided"
        else:
            if passphrase and len(passphrase):
                self.key = RSA.import_key(self.read_file(file_name, "r", self.root if not root else root).read(), passphrase=passphrase)
            else:
                self.key = RSA.import_key(self.read_file(file_name, "r", self.root if not root else root).read())
            self.cipher = PKCS1_OAEP.new(self.key)
            self.secret_key = self.cipher.decrypt(self.get_bytes(ed["secret_token"]))
            self.token = self.get_base64(self.secret_key)
            self.session_cipher = AES.new(self.secret_key, AES.MODE_EAX, nonce=self.get_bytes(ed["nonce"]))
            data = self.session_cipher.decrypt_and_verify(self.get_bytes(ed["ct"]), self.get_bytes(ed["tag"]))
            return data.decode(self.encoding)
        