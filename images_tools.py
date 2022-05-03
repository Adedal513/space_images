from os import remove
from os.path import split
from os.path import splitext
from pathlib import Path
from requests import get
from urllib.parse import unquote
from urllib.parse import urlsplit


def get_image_name_and_extension(url: str) -> (str, str):
    """
    Возвращает имя файла и его расширение

    :param url: URL-адрес изображения
    :return: имя файла и его расширение
    """
    unquoted_url = unquote(url)
    image_path = urlsplit(unquoted_url).path
    image = split(image_path)[1]

    image_name = splitext(image)[0]
    image_extension = splitext(image)[1]

    return image_name, image_extension


def download_image_by_url(url: str, target_directory: str):
    """
    Скачивает изображение в целевой каталог

    :param url: URL-адрес изображения
    :param target_directory: Целевая директоря для скачивания
    """
    file_name, file_extension = get_image_name_and_extension(url)

    response = get(url)
    response.raise_for_status()

    Path(target_directory).mkdir(parents=True, exist_ok=True)

    with open(f'{target_directory}/{file_name}{file_extension}', "wb") as file:
        file.write(response.content)


def clear_image_directories(image_directories: [Path]):
    """
    Удаляет все файлы в указанных директориях

    :param image_directories: Список адресов папок, где необходимо очистить файлы
    """
    for folder in image_directories:
        for image in folder.iterdir():
            remove(image)
