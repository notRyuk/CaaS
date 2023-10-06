import os
from io import TextIOWrapper, BufferedReader, BufferedWriter
from typing import Optional, Union, Literal



class DefaultService:

    def __init__(self, name: str, root: Optional[str] = None):
        self.name = name
        self.encoding = "utf-8"
        if root:
            self.root = root
        else:
            self.root = os.getcwd()
    
    def read_file(
        self, 
        file_name: str, 
        read_mode: Optional[type[Literal['r', 'rt', 'tr', 'U', 'rU', 'Ur', 'rtU', 'rUt', 'Urt', 'trU', 'tUr', 'Utr']]] = "r",
        root: Optional[str] = os.getcwd()
    ) -> Union[TextIOWrapper, BufferedReader, False]:
        path = os.path.join(root, file_name)
        if not os.path.isfile(path):
            return False
        return open(path, read_mode)
    
    def write_file(
        self,
        file_name: str, 
        read_mode: Optional[type[Literal['wb', 'bw', 'ab', 'ba', 'xb', 'bx']]] = "r",
        root: Optional[str] = os.getcwd()
    ) -> Union[TextIOWrapper, BufferedWriter, False]:
        path = os.path.join(root, file_name)
        if not os.path.isfile(path):
            return False
        return open(path, read_mode)

