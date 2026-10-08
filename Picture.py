import json
import os
import requests


class YandexDiskUploader:
    def __init__(self, token: str):
        self.base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.headers = {
            'Authorization': f'OAuth {token}',
            'Content-Type': 'application/json'
        }

    def create_folder(self, folder_name: str):
        params = {'path': folder_name}
        response = requests.put(self.base_url, headers=self.headers, params=params)
        # 201 - создана, 409 - уже существует
        if response.status_code in (201, 409):
            return True
        print(f"Ошибка при создании папки: {response.json().get('message')}")
        return False

    def upload_file(self, folder_name: str, file_name: str, file_content: bytes):
        upload_url_endpoint = f"{self.base_url}/upload"
        disk_path = f"{folder_name}/{file_name}"
        params = {'path': disk_path, 'overwrite': 'true'}

        # 1. Получаем ссылку для загрузки
        resp = requests.get(upload_url_endpoint, headers=self.headers, params=params)
        if resp.status_code != 200:
            print(f"Ошибка получения ссылки для загрузки: {resp.json().get('message')}")
            return False

        upload_url = resp.json().get('href')

        # 2. Отправляем байты файла по полученной ссылке
        put_resp = requests.put(upload_url, data=file_content)
        return put_resp.status_code == 201


def get_cat_image(text: str) -> bytes:
    # Получает изображение кота с текстом через API cataas.com
    url = f"https://cataas.com/cat/says/{text}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    raise Exception(f"Не удалось получить картинку: статус {response.status_code}")


def main():
    # 1. Ввод данных
    token = input("Введите токен Яндекс.Диска (Полигон): ").strip()
    text = input("Введите текст для картинки с котом: ").strip()
    

    if not token or not text:
        print("Ошибка: все поля должны быть заполнены.")
        return

    # 2. Получение картинки с котиком
    print("Получаем картинку кота...")
    image_bytes = get_cat_image(text)
    file_size = len(image_bytes)

    # 3. Имя файла на Яндекс.Диске
    file_name = f"{text}.jpg"

    # 4. Загрузка на Яндекс.Диск
    uploader = YandexDiskUploader(token)
    print(f"Создаем папку на Яндекс.Диске...")
    uploader.create_folder

    print(f"Загружаем файл '{file_name}'...")
    if uploader.upload_file(file_name, image_bytes):
        print("Файл успешно загружен на Яндекс.Диск!")

        # 5. Сохранение информации о файле в json
        info = [
            {
                "file_name": file_name,
                "size_bytes": file_size
            }
        ]

        json_file_name = "uploaded_cats_info.json"
        with open(json_file_name, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        print(f"Информация сохранена в файл {json_file_name}")
    else:
        print("Не удалось загрузить файл.")


if __name__ == '__main__':
    main()