import aiohttp

from plugin_system import Plugin

plugin = Plugin("Скриншот сайта",
                usage=["скрин [адрес сайта] - сделать скриншот сайта [адрес сайта]"])


# Желательно первой командой указывать основную (она будет в списке команд)
@plugin.on_command('скрин')
async def screen(msg, args):
    if not args:
        return msg.answer('Вы не указали сайт!')

    async with aiohttp.ClientSession() as sess:
        async with sess.get("http://api.s-shot.ru/1280x720/1280/png/?" + args.pop()) as resp:
            result = await msg.vk.upload_photo(await resp.read())

            return await msg.answer('Держи свой скрин :)', attachment=str(result))
