from datetime import datetime
from images_tools import download_image_by_url
from requests import get
from urllib.parse import urlencode


NASA_APOD_API_URL = "https://api.nasa.gov/planetary/apod"
NASA_EPIC_API_URL = "https://api.nasa.gov/EPIC/api/natural/images"
TARGET_DIRECTORY = './images/nasa_apod'


def fetch_nasa_apod(api_key: str, number_of_photos=1):
    """
    Скачивает последнее "Астрономическое изображение дня" APOD в директорию ./images/nasa_apod

    :param api_key: API-ключ NASA Web API
    :param number_of_photos: Число фотографий для скачивания
    """
    params = {"count": number_of_photos, "api_key": api_key}

    response = get(NASA_APOD_API_URL, params=params)
    response.raise_for_status()

    for image_data in response.json():
        image_url = image_data["url"]

        download_image_by_url(target_directory=TARGET_DIRECTORY, url=image_url)


def fetch_nasa_epic(api_key: str, number_of_photos=1):
    """
    Скачивает последнее изображение с камеры EPIC в директорию ./images/nasa_epic

    :param api_key: API-ключ
    :param number_of_photos: Число фотографий для скачивания
    """
    params = {"api_key": api_key}

    response = get(NASA_EPIC_API_URL, params=params)
    response.raise_for_status()

    images_info = response.json()

    for photo_num in range(number_of_photos):
        image_data = images_info[photo_num]

        image_name = image_data['image']
        image_date = datetime.strptime(image_data['date'], "%Y-%m-%d %H:%M:%S")

        year, month, day = image_date.year, str(image_date.month).zfill(2), str(image_date.day).zfill(2)

        image_request_url = f'https://api.nasa.gov/EPIC/archive/natural/{year}/{month}/{day}/png/{image_name}.png?'
        image_request_url = image_request_url + urlencode(params)

        download_image_by_url(target_directory='./images/nasa_epic', url=image_request_url)
