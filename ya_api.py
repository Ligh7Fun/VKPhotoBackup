import requests
from logger import Logger


class YandexUploader:

    _URL = 'https://cloud-api.yandex.net/v1/disk/resources'
    _UPLOAD = '/upload'
    _FOLDER = '/netology/'
    log = Logger()

    def __init__(self, access_token: str, folder: str) -> None:
        self.token = access_token
        self.folder = self._FOLDER + folder

    def _get_headers(self) -> dict:
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}',
        }

    def _get_folder(self):
        url = self._URL
        params = {
            'path': self.folder
        }
        response = requests.get(url=url, headers=self._get_headers(), params=params)
        return response

    def _create_folder(self) -> None:
        folder_response = self._get_folder()
        if folder_response.status_code == 404:
            self.log.log(f'Каталога {self.folder} нет, создаем.')
            url = self._URL
            params = {
                'path': self.folder,
            }
            response = requests.put(url=url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            self.log.log(f'Каталог {self.folder} создан.')
        else:
            self.log.log(f'Каталог {self.folder} уже есть.')
            folder_response.raise_for_status()

    def upload_files(self, files_list: list) -> None:
        self._create_folder()
        url = self._URL + self._UPLOAD

        for file_info in files_list:
            file_name = file_info[0]
            file_url = file_info[1]

            path_to_file = self.folder + '/' + file_name

            params = {
                'path': path_to_file,
                'url': file_url,
                'overwrite': 'false',
            }
            response = requests.post(url=url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            self.log.log(f'Файл {path_to_file} загружен на Яндекс.Диск.')
