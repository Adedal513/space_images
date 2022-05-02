from os import getenv
from requests import get
from pathlib import Path
from urllib.parse import urlsplit, unquote, urlencode
from os.path import split, splitext
from dotenv import load_dotenv
from datetime import datetime
import telegram


spacex_api_url = "https://api.spacexdata.com/v4/launches/"
nasa_apod_api_url = "https://api.nasa.gov/planetary/apod"
nasa_epic_api_url = "https://api.nasa.gov/EPIC/api/natural/images"


def get_image_name_and_extension(url: str) -> (str, str):
    unquoted_url = unquote(url)
    image_path = urlsplit(unquoted_url).path
    image = split(image_path)[1]

    image_name = splitext(image)[0]
    image_extension = splitext(image)[1]

    return image_name, image_extension


def download_image_by_url(url: str):
    file_name, file_extension = get_image_name_and_extension(url)
    response = get(url)
    response.raise_for_status()

    Path("./images/").mkdir(parents=True, exist_ok=True)

    with open(f"./images/{file_name}{file_extension}", "wb") as file:
        file.write(response.content)


def fetch_spacex_last_launch():
    response = get(spacex_api_url)
    response.raise_for_status()

    launches = response.json()

    for launch in reversed(launches):
        links = launch["links"]["flickr"]

        if links["original"] or links["small"]:
            launch_photos = []

            if links["original"]:
                launch_photos = links["original"]
            elif links["small"]:
                launch_photos = links["small"]

            for photo_link in launch_photos:
                download_image_by_url(photo_link)

            break


def fetch_nasa_apod(number_of_photos: int, api_key: str):
    params = {"count": number_of_photos, "api_key": api_key}

    response = get(nasa_apod_api_url, params=params)
    response.raise_for_status()

    for image_data in response.json():
        image_url = image_data["url"]

        download_image_by_url(image_url)


def fetch_nasa_epic(number_of_photos: int, api_key: str):
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

        download_image_by_url(image_request_url)


if __name__ == "__main__":

    load_dotenv()
    nasa_api_key = getenv("NASA_API_KEY")
    telegram_bot_token = getenv("TELEGRAM_BOT_TOKEN")
    chat_id = getenv("CHAT_ID")
    
    bot = telegram.Bot(token=telegram_bot_token)

    bot.send_message(
        chat_id=chat_id,
        text="Hello, world!"
    )
