import os
from io import TextIOWrapper, BufferedReader, BufferedWriter
from typing import Optional, Union, Literal
from base64 import b64decode, b64encode
from CaaS.config import ROOTDIR


class DefaultService:

    def __init__(self, name: str, root: Optional[str] = None):
        self.name = name
        self.encoding = "utf-8"
        self.chunk_size = 96
        if root:
            self.root = root
        else:
            self.root = ROOTDIR
    
    def read_file(
        self, 
        file_name: str, 
        read_mode: Optional[type[Literal['r', 'rt', 'tr', 'U', 'rU', 'Ur', 'rtU', 'rUt', 'Urt', 'trU', 'tUr', 'Utr']]] = "r",
        root: Optional[str] = None
    ) -> Union[TextIOWrapper, BufferedReader, bool]:
        path = os.path.join(root, file_name)
        
        if not os.path.isfile(path):
            return False
        return open(path, read_mode)
    
    def write_file(
        self,
        file_name: str, 
        write_mode: Optional[type[Literal['wb', 'bw', 'ab', 'ba', 'xb', 'bx']]] = "w",
        root: Optional[str] = os.getcwd()
    ) -> Union[TextIOWrapper, BufferedWriter]:
        path = os.path.join(root, file_name)
        return open(path, write_mode)

    def is_file(self, file_name: str, root: Optional[str] = os.getcwd()) -> bool:
        return os.path.isfile(os.path.join(root, file_name))

    def get_base64(self, b: bytes) -> str:
        return b64encode(b).decode(self.encoding)

    def get_bytes(self, s: str) -> bytes:
        return b64decode(s)

