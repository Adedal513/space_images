import os

import telegram

from datetime import datetime
from dotenv import load_dotenv
from os import getenv
from os import listdir
from os.path import split
from os.path import splitext
from pathlib import Path
from requests import get
from time import sleep
from urllib.parse import unquote
from urllib.parse import urlencode
from urllib.parse import urlsplit


spacex_api_url = "https://api.spacexdata.com/v4/launches/"
nasa_apod_api_url = "https://api.nasa.gov/planetary/apod"
nasa_epic_api_url = "https://api.nasa.gov/EPIC/api/natural/images"
image_categories = [
    'spacex',
    'apod',
    'epic'
]
image_directories = {
    'spacex': Path('./images/spacex_launches'),
    'apod': Path('./images/nasa_apod'),
    'epic': Path('./images/nasa_epic')
}


def get_image_name_and_extension(url: str) -> (str, str):
    unquoted_url = unquote(url)
    image_path = urlsplit(unquoted_url).path
    image = split(image_path)[1]

    image_name = splitext(image)[0]
    image_extension = splitext(image)[1]

    return image_name, image_extension


def download_image_by_url(url: str, target_directory: str):
    file_name, file_extension = get_image_name_and_extension(url)

    response = get(url)
    response.raise_for_status()

    Path(target_directory).mkdir(parents=True, exist_ok=True)

    with open(f'{target_directory}/{file_name}{file_extension}', "wb") as file:
        file.write(response.content)


def fetch_spacex_last_launch():
    response = get(spacex_api_url)
    response.raise_for_status()

    launches = response.json()

    for launch in reversed(launches):
        links = launch["links"]["flickr"]
        launch_photos = []

        if links['original'] or links['small']:
            if links['small']:
                launch_photos = links['small']
            elif links['original']:
                launch_photos = links['original']

            for photo_link in launch_photos:
                download_image_by_url(target_directory='./images/spacex_launches', url=photo_link)

            break


def fetch_nasa_apod(api_key: str, number_of_photos=1):
    params = {"count": number_of_photos, "api_key": api_key}

    response = get(nasa_apod_api_url, params=params)
    response.raise_for_status()

    for image_data in response.json():
        image_url = image_data["url"]

        download_image_by_url(target_directory='./images/nasa_apod', url=image_url)


def fetch_nasa_epic(api_key: str, number_of_photos=1):
    params = {"api_key": api_key}

    response = get(nasa_epic_api_url, params=params)
    response.raise_for_status()

    images_info = response.json()

    for i in range(number_of_photos):
        image_data = images_info[i]

        image_name = image_data['image']
        image_date = datetime.strptime(image_data['date'], "%Y-%m-%d %H:%M:%S")

        year, month, day = image_date.year, str(image_date.month).zfill(2), str(image_date.day).zfill(2)

        image_request_url = f'https://api.nasa.gov/EPIC/archive/natural/{year}/{month}/{day}/png/{image_name}.png?'
        image_request_url = image_request_url + urlencode(params)

        download_image_by_url(target_directory='./images/nasa_epic', url=image_request_url)


def post_pictures_with_title(tg_bot: telegram.Bot, tg_chat_id: str, images_path: Path, text: str):
    images_count = 1
    total_images = len(listdir(images_path))

    for image in images_path.iterdir():
        with open(image, 'r') as file:
            caption_text = f'{text}\n{images_count}/{total_images}'
            images_count += 1

            tg_bot.send_photo(
                chat_id=tg_chat_id,
                caption=caption_text,
                photo=file.buffer
            )


def clear_image_directories():
    for folder in image_directories.values():
        for image in folder.iterdir():
            os.remove(image)


if __name__ == "__main__":

    load_dotenv()
    nasa_api_key = getenv("NASA_API_KEY")
    telegram_bot_token = getenv("TELEGRAM_BOT_TOKEN")
    chat_id = getenv("CHAT_ID")
    posting_frequency = int(getenv('IMAGE_POSTING_FREQUENCY'))

    bot = telegram.Bot(token=telegram_bot_token)

    while True:
        fetch_nasa_epic(api_key=nasa_api_key)
        fetch_nasa_apod(api_key=nasa_api_key)
        fetch_spacex_last_launch()

        today_date = datetime.today().date()

        captions = {
            'spacex': 'SpaceX last successful launch',
            'apod': f'NASA Astronomic Picture of the Day\n{today_date}',
            'epic': f'Latest Earth photo from the orbit\n{today_date}'
        }

        for category in image_categories:
            post_pictures_with_title(
                tg_bot=bot,
                tg_chat_id=chat_id,
                images_path=image_directories[category],
                text=captions[category]
            )

        clear_image_directories()

        sleep(posting_frequency)
