from datetime import datetime
from os import getenv, listdir, remove
from pathlib import Path
from time import sleep

import telegram
from dotenv import load_dotenv

from fetch_nasa import fetch_nasa_apod, fetch_nasa_epic
from fetch_spacex import fetch_spacex_last_launch


IMAGE_DIRECTORIES = {
    'spacex': Path('./images/spacex_launches'),
    'apod': Path('./images/nasa_apod'),
    'epic': Path('./images/nasa_epic')
}


def post_pictures_with_title(tg_bot: telegram.Bot, tg_chat_id: str, images_path: Path, text: str):
    """
    Выкладывает изображения в указанный канал с указанными подписями

    :param tg_bot: объект telegram-бота
    :param tg_chat_id: ID канала для выкладывания фотографий
    :param images_path: путь к изображениям
    :param text: Основная подпись для изображений
    """
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


def clear_image_directories(image_directories: [Path]):
    """
    Удаляет все файлы в указанных директориях

    :param image_directories: Список адресов папок, где необходимо очистить файлы
    """
    for folder in image_directories:
        for image in folder.iterdir():
            remove(image)


if __name__ == "__main__":

    load_dotenv()
    nasa_api_key = getenv("NASA_API_KEY")
    telegram_bot_token = getenv("TELEGRAM_BOT_TOKEN")
    posting_frequency = int(getenv('IMAGE_POSTING_FREQUENCY'))
    chat_id = getenv('CHAT_ID')

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

        for category in IMAGE_DIRECTORIES.keys():
            post_pictures_with_title(
                tg_bot=bot,
                tg_chat_id=chat_id,
                images_path=IMAGE_DIRECTORIES[category],
                text=captions[category]
            )

        clear_image_directories(IMAGE_DIRECTORIES.values())

        sleep(posting_frequency)
