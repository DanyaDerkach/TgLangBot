from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

import keyboards as kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"""
Hello, {message.from_user.full_name}!

🧠 Що я вмію:
• Перевіряти переклади слів (ENG→UA, UA→ENG)
• Проводити тести з варіантами відповіді
• Працювати з рівнями A1–C2

Обери, з чого хочеш почати:
• /level — обрати рівень складності
• /mode — вибрати режим гри або тесту
• /help — довідка""", reply_markup=kb.main)

@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer("""
Ось доступні команди:

/start — перезапускає роботу бота
/level — вибрати рівень англійської мови
/test — розпочати тестування з варіантами відповіді
/quiz — розпочати тестування з відкритою відповіддю
/help — довідка""")

@router.message(F.text == '✏️ Тестування')
async def start_test(message: Message):
    (await message.answer("Виберіть режим перекладу:", reply_markup=kb.language))

@router.callback_query(F.data == 'engtoua')
async def test_engtoua(callback: CallbackQuery):
    for i in range(0, 9):
        await callback.message.edit_text("/10\nЯк перекладається слово:", reply_markup=kb.language)