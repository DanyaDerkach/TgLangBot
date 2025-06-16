import asyncio
import logging
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram import Bot, Dispatcher

from config import API_TOKEN

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Hello, {message.from_user.full_name}!\n\n🧠 Що я вмію:\n• Перевіряти переклади слів (ENG→UA, UA→ENG)\n• Проводити тести з варіантами відповіді\n• Працювати з рівнями A1–C2\n\nОбери, з чого хочеш почати:\n• /level — обрати рівень складності\n• /mode — вибрати режим гри або тесту\n• /help — довідка")

@dp.message(Command('help'))
async def get_help(message: Message):
    await message.answer("Ось доступні команди:\n\n/start — перезапускає роботу бота\n/level — вибрати рівень англійської мови\n/test — розпочати тестування з варіантами відповіді\n/quiz — розпочати тестування з відкритою відповіддю\nhelp — довідка")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')