# Space Telegram

---

Файл регулярно выкладывает в Telegram-канал [@SpaceBotTesting](https://t.me/space_bot_testing):

- Изображение [Astronomic Picture of the Day](https://epic.gsfc.nasa.gov/) от NASA
- Изображение планеты Земля с камеры [EPIC](https://epic.gsfc.nasa.gov/)
- Фотографии последнего запуска аппаратов SpaceX

### Как установить

Python3 должен быть уже установлен. Затем используйте pip (или pip3, есть есть конфликт с Python2) для установки зависимостей:

```pip install -r requirements.txt```

Для работы скрипту необходим `.env` файл с переменными окружения:

```shell
NASA_API_KEY=<api_ключ_NASA>
TELEGRAM_BOT_TOKEN=<токен_бота>
IMAGE_POSTING_FREQUENCY=86400
```

`NASA_API_KEY` - ключ для Web API NASA\
`TELEGRAM_BOT_TOKEN` - токен для доступа к HTTP API бота\
`IMAGE_POSTING_FREQUENCY` - частота публикации фотографий **в секундах** (по умолчанию - раз в сутки)

### Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).