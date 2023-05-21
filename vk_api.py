import requests


class VK:

    def __int__(self, access_token: str, version: str = '5.131') -> None:
        self.access_token = access_token
        self.version = version
        self.params = {'access_token': self.access_token, 'v': self.version}
