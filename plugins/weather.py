import time

import aiohttp
import hues

from plugin_system import Plugin
from utils import schedule_coroutine

plugin = Plugin("Погода",
                usage="погода - погода (название города необходимо писать на английском!)")

# сервис для определения погоды: http://openweathermap.org/api
# введите свой ключ, если будете использовать!
code = "fe198ba65970ed3877578f728f33e0f9"
default_city = "Москва"


text_to_days = {"завтра": 1, "послезавтра": 2, "через день": 2, "через 1 день": 2,
                "через 2 дня": 3, "через 3 дня": 4, "через 4 дня": 5,  "через 5 дней": 6,
                "через 6 дней": 7, "через 7 дней": 8}

if code == "fe198ba65970ed3877578f728f33e0f9":
    hues.warn("Вы используете общественный ключ для openweathermap.org! Рекомендуем вам получить личный!")


@plugin.on_init()
async def init(vk):
    plugin.temp_data["weather"] = {}

    schedule_coroutine(clear_cache())


@plugin.schedule(10800)  # 3 часа
async def clear_cache(stopper):
    plugin.temp_data["weather"] = {}


@plugin.on_command('погода')
async def weather(msg, args):
    city = default_city
    days = 0

    if args:
        arguments = " ".join(args)

        for k, v in sorted(text_to_days.items(), key=lambda x: -len(x[0])):
            if k in arguments:
                arguments = arguments.replace(k, "")

                days = v

        possible_city = arguments.replace(" в ", "")

        if possible_city:
            city = possible_city

    if f"{city}{days}" in plugin.temp_data["weather"]:
        return await msg.answer(plugin.temp_data["weather"][f"{city}{days}"])

    if days == 0:
        url = f"http://api.openweathermap.org/data/2.5/weather?APPID={code}&lang=ru&q={city}"
    else:
        url = f"http://api.openweathermap.org/data/2.5/forecast/daily?APPID={code}&lang=ru&q={city}&cnt={days + 1}"

    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as resp:
            response = await resp.json()

            if "cod" in response and response["cod"] == '404':
                return await msg.answer("Город не найден! Может быть, вы написали название города на русском?🤔")

            if days != 0:
                answer = f"{city}. Погода.\n\n"

                for i in range(1, len(response["list"])):
                    day = response["list"][i]
                    temperature = day["temp"]["day"] - 273
                    humidity = day["humidity"]
                    description = day["weather"][0]["description"]
                    wind = day["speed"]
                    cloud = day["clouds"]
                    date = time.strftime("%Y-%m-%d", time.gmtime(day["dt"]))

                    answer += (f'{date}:\n'
                               f'{description[0].upper()}{description[1:]}\n'
                               f'Температура: {round(temperature, 2)} °C\n'
                               f'Влажность: {humidity} %\n'
                               f'Облачность: {cloud} %\n'
                               f'Скорость ветра: {wind} м/с\n\n')

                plugin.temp_data["weather"][f"{city}{days}"] = answer

                return await msg.answer(answer)
            else:
                result = response

                description = result["weather"][0]["description"]
                temperature = result["main"]["temp"] - 273
                humidity = result["main"]["humidity"]
                wind = result["wind"]["speed"]
                cloud = result["clouds"]["all"]

                answer = (f'{city}. Текущая погода.\n'
                          f'{description[0].upper()}{description[1:]}\n'
                          f'Температура: {round(temperature, 2)} °C\n'
                          f'Влажность: {humidity} %\n'
                          f'Облачность: {cloud} %\n'
                          f'Скорость ветра: {wind} м/с')

                plugin.temp_data["weather"][f"{city}{days}"] = answer

                return await msg.answer(answer)
