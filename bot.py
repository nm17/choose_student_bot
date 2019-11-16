import random

import dotenv
import aiogram
import tinydb
from aiogram import types
from aiogram.utils import executor
from loguru import logger
from tinydb import Query
from tinydb.operations import set as set_
import parse

env = dotenv.dotenv_values()

db = tinydb.TinyDB("botdb.json")

bot = aiogram.Bot(env["BOT_TOKEN"], proxy=env["PROXY"])
dp = aiogram.Dispatcher(bot)

HELP_TEXT = """Мои комманды:

`/add <имя>` - добавляет ученика в список
`/list` - показывает список учеников
`/edit "<старое_имя>" "<новое_имя>"` - изменяет имя ученика
`/delete <имя>` - удаляет ученика из списка
`/choose` - выдает случайный список учеников
"""


@dp.message_handler(commands=["help", "start"])
async def help_(message: types.Message):
    await message.reply(HELP_TEXT, parse_mode="markdown")


@dp.message_handler(commands=["add"])
async def add(message: types.Message):
    name = parse.parse("/add {}", message.text)[0]
    db.insert({"user_id": message.from_user.id, "name": name})
    logger.debug(
        "Добавил ученика {name} от пользователя {user_name} ({user_id})",
        name=name,
        user_name=message.from_user.username,
        user_id=message.from_user.id,
    )
    await message.reply("Ученик добавлен")


@dp.message_handler(commands=["edit"])
async def edit(message: types.Message):
    name_old, name_new = parse.parse('/edit "{}" "{}"', message.text)
    q = Query()
    db.update(
        set_("name", name_new),
        (q.name == name_old) & (q.user_id == message.from_user.id),
    )
    await message.reply("Ученик изменен")


@dp.message_handler(commands=["list"])
async def list_(message: types.Message):
    q = Query()
    result = db.search(q.user_id == message.from_user.id)
    result = "\n".join([n["name"] for n in result])
    await message.reply("Вот ваши ученики: \n" + result)


@dp.message_handler(commands=["delete"])
async def delete(message: types.Message):
    name = parse.parse("/delete {}", message.text)[0]
    q = Query()
    db.remove((q.name == name) & (q.user_id == message.from_user.id))
    await message.reply("Ученик удален")


@dp.message_handler(commands=["choose"])
async def choose(message: types.Message):
    q = Query()
    results = [
        str(i + 1) + ". " + n["name"]
        for i, n in enumerate(db.search(q.user_id == message.from_user.id))
    ]
    random.SystemRandom().shuffle(results)
    await message.reply("Список выбранных учеников: \n" + "\n".join(results))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
