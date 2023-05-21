import requests


class VK:
    """

    Args:
        access_token
        user_id
        version
    """

    def __init__(
            self,
            access_token: str,
            user_id: str,
            version: str = '5.131'
    ) -> None:
        self.access_token = access_token
        self.user_id = user_id
        self.version = version
        self.params = {'access_token': self.access_token, 'v': self.version}

    def get_photos(
            self,
            album_id: str = 'profile',
            extended: int = 1,
            photo_sizes: int = 1,
            count: int = 5
    ) -> dict:
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'owner_id': self.user_id,
            'album_id': album_id,
            'extended': extended,
            'photo_sizes': photo_sizes,
            'count': count,
        }
        response = requests.get(url, params={**self.params, **params})
        response.raise_for_status()
        response_json = response.json()
        print(len(response_json['response']['items']))

        return response_json
