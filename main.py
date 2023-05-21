import requests
from dotenv import load_dotenv
import json
import os
from logger import Logger
from vk_api import VK
from pprint import pprint


class Backup:

    def __init__(self):
        self.image_likes = set()

    def set_image_name(
            self,
            image: dict,
            image_url: str
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
        image_ext = image_url[image_url.rfind('.'):image_url.find('?')]
        image_name += image_ext
        log.log(f'Назначено имя файла {image_name}')

        return image_name

    def get_images(self, photos_json: dict) -> list:
        """
        Получение списка изображений (image_name, image_url, size)
        """
        images_url = []
        photos = photos_json.get('response', {})
        if photos.get('count'):
            for item in photos.get('items', []):
                image_url = item['sizes'][-1]['url']
                image_name = self.set_image_name(item, image_url)
                image_size = item['sizes'][-1]['type']
                images_url.append((image_name, image_url, image_size))
        else:
            log.log('Изображения не найдены.')
            raise Exception('Изображения не найдены')
        self.image_likes.clear()
        log.log('Список изображений получен.')
        return images_url

    @staticmethod
    def save_json_file(images_url: list, indent: int = 4) -> None:
        """
         Создание json файла с информацией по файлам
        """
        photos_save = []
        file_name = 'VKPhotoBackup.json'
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
                log.log(f'Файл {image_name} уже есть в папке.')

    def start_backup(self):
        pass


if __name__ == '__main__':
    load_dotenv()
    VK_TOKEN = os.getenv('VK_TOKEN')
    YA_TOKEN = os.getenv('YA_TOKEN')
    USER_ID = os.getenv('USER_ID')
    log = Logger()
    vk = VK(VK_TOKEN, USER_ID)
    photos_list = vk.get_photos(count=12)
    back = Backup()
    back_get_img = back.get_images(photos_list)
    back.save_json_file(back_get_img)
    back.save_photos_local(back_get_img)
