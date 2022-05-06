from requests import get
from images_tools import download_image_by_url


SPACEX_API_URL = "https://api.spacexdata.com/v4/launches/"


def fetch_spacex_last_launch():
    """
    Скачивает последние доступные фотографии с запуска аппаратов SpaceX.
    Отдает предпочтение файлам малого размера.
    """
    response = get(SPACEX_API_URL)
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
