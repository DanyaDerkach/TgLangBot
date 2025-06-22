from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from functools import wraps

import keyboards as kb

router = Router()

class QuizState(StatesGroup):
    testing = State()
    level = State()
    quiz = State()

def no_state():
    def decorator(handler):
        @wraps(handler)
        async def wrapper(message: Message, state: FSMContext, *args, **kwargs):
            current_state = await state.get_state()
            if current_state:
                await message.answer("🚫 Ця дія зараз не доступна.\nНапишіть /exit, щоб вийти.")
                return
            return await handler(message, state, *args, **kwargs)
        return wrapper
    return decorator

@router.message(Command("exit"))
async def cmd_start(message: Message, state: FSMContext, callback: CallbackQuery):
    await state.set_state(None)
    await callback.message.edit_reply_markup(reply_markup=None)
    await message.answer(f"", reply_markup=kb.main)

@router.message(CommandStart())
@no_state()
async def cmd_start(message: Message, state: FSMContext):
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

@router.message(Command("help"))
@no_state()
async def get_help(message: Message, state: FSMContext):
    await message.answer("""
Ось доступні команди:

/start — перезапускає роботу бота
/level — вибрати рівень англійської мови
/test — розпочати тестування з варіантами відповіді
/quiz — розпочати тестування з відкритою відповіддю
/help — довідка""")

@router.message(F.text == "❔ Довідка")
@no_state()
async def get_help(message: Message, state: FSMContext):
    await message.answer("""
Ось доступні команди:

/start — перезапускає роботу бота
/level — вибрати рівень англійської мови
/test — розпочати тестування з варіантами відповіді
/quiz — розпочати тестування з відкритою відповіддю
/help — довідка""")

@router.message(F.text =='💪 Складність')
@no_state()
async def start_test(message: Message, state: FSMContext):
    await state.set_state(QuizState.level)
    await message.answer("Виберіть складність:", reply_markup=kb.level)

@router.message(QuizState.level)
async def level_chosen(message: Message, state: FSMContext):
    text = message.text.strip()
    valid = {"A1", "A2", "B1","B2", "C1", "C2"}
    parts = text.split()
    level = parts[-1] if len(parts) > 0 else ""
    if level not in valid:
        await message.answer("❌ Невідомий рівень.")
        return
    await state.update_data(level=level)
    await message.answer(f"✅ Рівень {level} обрано.", reply_markup=kb.main)
    await state.set_state(None)

@router.message(F.text == '✏️ Тестування')
@no_state()
async def start_test(message: Message, state: FSMContext):
    await message.answer("Виберіть режим перекладу:", reply_markup=kb.language)

@router.callback_query(F.data.in_(["eng_to_ua", "ua_to_eng"]))
async def select_mode(callback: CallbackQuery, state: FSMContext):

    await state.set_state(QuizState.testing)
    level = (await state.get_data()).get("level", "A1")
    word, correct_answer, keyboard = kb.generate_question(level)
    await state.update_data(correct=correct_answer)

    await callback.message.edit_text(f"🔤 Як перекладається слово: {word}?", reply_markup=keyboard)

@router.callback_query(F.data.startswith("answer_"))
async def check_answer(callback: CallbackQuery, state: FSMContext):
    selected = callback.data.split("_", 1)[1]
    data = await state.get_data()
    correct = data.get("correct")
    points = 0
    if selected == correct:
        result = "✅ Правильно!\n\n"
        points = points + 1
    else:
        result= f"❌ Неправильно. Правильна відповідь: {correct}\n\n"

    level = (await state.get_data()).get("level", "A1")
    word, correct_answer, keyboard = kb.generate_question(level)
    await state.update_data(correct=correct_answer)
    await callback.message.edit_text(f"{result}🔤 Як перекладається слово: {word}?", reply_markup=keyboard)

#@router.message(F.text == '💬 Вікторина')
#async def start_test(message: Message):
#    await message.answer("Виберіть режим перекладу:", reply_markup=kb.language)
