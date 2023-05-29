import requests
from logger import Logger


class VK:
    _URL = 'https://api.vk.com/method/'
    _PHOTOS = 'photos.get'
    _ALBUMS = 'photos.getAlbums'
    _RESOLVE = 'utils.resolveScreenName'
    log = Logger()

    def __init__(
            self,
            access_token: str,
            version: str = '5.131'
    ) -> None:
        self.access_token = access_token
        self.version = version
        self.params = {'access_token': self.access_token, 'v': self.version}

    def get_albums(self, user_id) -> dict:
        url = self._URL + self._ALBUMS
        params = {
            'owner_id': user_id,
            'need_system': 1
        }

        response = requests.get(url, params={**self.params, **params})
        response.raise_for_status()
        response_json = response.json()

        if response_json.get('error'):
            raise Exception('Приватный профиль, нет возможности скачать фото')

        return response_json

    def get_user_id(self, screen_name: str) -> int:
        """
        Метод для получения USER_ID по короткому имени.
        :param screen_name: Короткое имя пользователя.
        :return: Возвращает USER_ID.
        """

        url = self._URL + self._RESOLVE
        params = {
            'screen_name': screen_name
        }

        response = requests.get(url, params={**self.params, **params})
        response.raise_for_status()
        response_json = response.json()

        if not response_json.get('response') != []:
            raise Exception('Для указанного значения нет USER_ID')

        return response_json.get('response').get('object_id')

    def get_photos(
            self,
            user_id: str,
            album_id: str = 'profile',
            extended: int = 1,
            photo_sizes: int = 1,
            count: int = 5
    ) -> dict:
        """
        Метод для получения фотографий пользователя ВКонтакте
        :return: Словарь с информацией о фотографиях пользователя
        """
        url = self._URL + self._PHOTOS
        params = {
            'owner_id': user_id,
            'album_id': album_id,
            'extended': extended,
            'photo_sizes': photo_sizes,
            'count': count,
        }

        response = requests.get(url, params={**self.params, **params})
        response.raise_for_status()
        response_json = response.json()
        if response_json.get('error'):
            raise Exception('Приватный профиль, нет возможности скачать фото.')

        return response_json
