import requests
from dotenv import load_dotenv
import json
import os
from logger import Logger
from vk_api import VK
from ya_api import YandexUploader


class VKBackup:

    def __init__(self):
        self.image_likes = set()

    def _set_image_name(self, image: dict) -> str:
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
        """
        Метод для получения списка альбомов, их заголовков и количества фото
        """
        albums = []
        album = albums_json.get('response', {})
        if album.get('count'):
            for item in album.get('items', []):
                albums.append((item['id'], item['title'], item['size']))
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
                    log.log(f'Файл {image_name} сохранен на локальном диске.')
            else:
                log.log(f'Файл {image_name} уже есть на локальном диске, пропускаем.')


if __name__ == '__main__':
    load_dotenv()  # Получаем токены и user_id из файла .env
    VK_TOKEN = os.getenv('VK_TOKEN')
    YA_TOKEN = os.getenv('YA_TOKEN')
    USER_ID = os.getenv('USER_ID')
    log = Logger()
    backup = VKBackup()
    vk = VK(VK_TOKEN, USER_ID)
    ya_disk = YandexUploader(YA_TOKEN, 'download_folder_' + USER_ID)

    my_albums = vk.get_albums()  # Получаем словарь с альбомами
    albums_list = backup.get_album_list(my_albums)  # Получаем список альбомов и их названия
    print('Для скачивания доступны следующие альбомы:')
    for index, album in enumerate(albums_list, start=1):
        print(f'{index}. {album[1]} ({album[2]} фото)')
    album_id = int(input('\nНомер альбома для скачивания: '))
    count_photo = int(input('Сколько фото скачать(по умолчанию = 5): ') or 5)
    try:
        # Фотографии с выбранного альбома
        photos_album = vk.get_photos(album_id=albums_list[album_id-1][0], count=count_photo)
        img_url = backup.get_images(photos_album)  # Список ссылок на фотографии
        ya_disk.upload_files(img_url)  # Загружаем файлы из альбома на диск
        backup.save_json_file(img_url, file_name='VKPhotoBackup.json')  # Json-файл с информацией по файлу
        backup.save_photos_local(img_url)  # Скачать файлы и на локальный диск
    except IndexError:
        log.log('Некорректно указан ID альбома.')
