import requests
from dotenv import load_dotenv
import json
import os
from logger import Logger
from vk_api import VK
from pprint import pprint
from ya_api import YandexUploader


class Backup:

    def __init__(self):
        self.image_likes = set()

    def _set_image_name(
            self,
            image: dict
    ) -> str:
        """
        Возвращает имя изображения по количеству лайков,
        если количество лайков совпадает, добавляет дату загрузки
        """
        image_like = image['likes']['count']
        image_name = str(image_like)
        if image_like in self.image_likes:
            image_name += '_' + str(image['date'])
        self.image_likes.add(image_like)
        image_name += '.jpg'
        log.log(f'Назначено имя файла {image_name}')

        return image_name

    @staticmethod
    def get_album_list(albums_json: dict) -> list:
        albums = []
        album = albums_json.get('response', {})
        if album.get('count'):
            for item in album.get('items', []):
                albums.append(item['id'])
        else:
            log.log('Альбомы не найдены.')
            raise Exception('Альбомы не найдены')
        return albums

    def get_images(self, photos_json: dict) -> list:
        """
        Получение списка изображений (image_name, image_url, size)
        """
        images_url = []
        photos = photos_json.get('response', {})
        if photos.get('count'):
            for item in photos.get('items', []):
                image_url = item['sizes'][-1]['url']
                image_name = self._set_image_name(item)
                image_size = item['sizes'][-1]['type']
                images_url.append((image_name, image_url, image_size))
        else:
            log.log('Изображения не найдены.')
            raise Exception('Изображения не найдены')
        self.image_likes.clear()
        log.log('Список изображений получен.')
        return images_url

    @staticmethod
    def save_json_file(images_url: list, file_name: str = 'VKPhotoBackup.json', indent: int = 4) -> None:
        """
         Создание json файла с информацией по файлам
        """
        photos_save = []
        for image_name, _, image_size in images_url:
            image = {
                'file_name': image_name,
                'size': image_size
            }
            photos_save.append(image)
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(photos_save, file, ensure_ascii=False, indent=indent)
            log.log(f'Файл {file_name} успешно сохранен.')

    @staticmethod
    def save_photos_local(images_url: list) -> None:
        """
        Сохранение изображений на локальный диск
        """
        user_folder = f'downloads_folder_{USER_ID}'

        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        for image_name, image_url, _ in images_url:
            filepath = os.path.join(user_folder, image_name)
            response = requests.get(image_url)
            if not os.path.isfile(filepath):
                with open(filepath, 'wb') as file:
                    file.write(response.content)
                    log.log(f'Файл {image_name} сохранен.')
            else:
                log.log(f'Файл {image_name} уже есть в локальной папке, пропускаем.')

    def start_backup(self):
        pass


if __name__ == '__main__':
    load_dotenv()
    VK_TOKEN = os.getenv('VK_TOKEN')
    YA_TOKEN = os.getenv('YA_TOKEN')
    USER_ID = os.getenv('USER_ID')
    log = Logger()
    vk = VK(VK_TOKEN, USER_ID)
    ya_disk = YandexUploader(YA_TOKEN, 'folder_'+USER_ID)
    my_albums = vk.get_albums()  # Получаем словарь с альбомами


    back = Backup()
    albums_list = back.get_album_list(my_albums)
    # print(vk.get_user_id('keep3r_str'))
    photos_album = vk.get_photos(album_id='-6', count=100)  # фотографии с альбома
    image_url = back.get_images(photos_album)  # Список ссылок на фотографии
    # pprint(image_url)
    # print()
    ya_disk.upload_files(image_url)

    # back.save_json_file(image_url, file_name='VKPhotoBackup.json')
    # back.save_photos_local(image_url)
