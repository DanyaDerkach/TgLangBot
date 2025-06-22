from aiogram import Router, F, Bot
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
                await message.answer("🚫 Ця дія зараз не доступна.")
                return
            return await handler(message, state, *args, **kwargs)
        return wrapper
    return decorator

@router.message(CommandStart())
@no_state()
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(f"""
Hello, {message.from_user.full_name}!

Вивчи пару слів легко через швидке тестування 🎯
Обери дію з меню нижче 👇""", reply_markup=kb.main)

@router.message(Command("help"))
@no_state()
async def get_help(message: Message, state: FSMContext):
    await message.answer("""
Бот допоможе вам вивчати слова англійською та українською в інтерактивній формі.
📋 Команди та кнопки:

🔹 /start — запустити або перезапустити бота
🔹 ❔ Довідка — показати це повідомлення
🔹 💪 Складність — вибір рівня знань: A1, A2, B1, B2, C1, C2
🔹 ✏️ Тестування — почати тест: переклад слів з англійської або з української
🔹 Завершити тестування — зупинити тестування вручну""")

@router.message(F.text == "❔ Довідка")
@no_state()
async def get_help(message: Message, state: FSMContext):
    await message.answer("""
Бот допоможе вам вивчати слова англійською та українською в інтерактивній формі.
📋 Команди та кнопки:

🔹 /start — запустити або перезапустити бота
🔹 ❔ Довідка — показати це повідомлення
🔹 💪 Складність — вибір рівня знань: A1, A2, B1, B2, C1, C2
🔹 ✏️ Тестування — почати тест: переклад слів з англійської або з української
🔹 Завершити тестування — зупинити тестування вручну""")

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
    sent = await message.answer("Виберіть режим перекладу:", reply_markup=kb.language)
    await state.update_data(select_mode_msg_id=sent.message_id)

@router.callback_query(F.data.in_(["eng_to_ua", "ua_to_eng"]))
async def select_mode(callback: CallbackQuery, state: FSMContext):
    mode = callback.data
    await state.set_state(QuizState.testing)
    level = (await state.get_data()).get("level", "A1")
    await state.update_data(mode=mode)
    word, correct_answer, keyboard = kb.generate_question(level, mode)
    await state.update_data(correct=correct_answer)
    sent = await callback.message.answer("Тестування розпочато", reply_markup=kb.exit_test)
    await callback.message.edit_text(f"🔤 Як перекладається слово: {word}?", reply_markup=keyboard)
    await state.update_data(
        test_started_msg_id=sent.message_id,
        test_question_msg_id=callback.message.message_id
    )
    await callback.answer()

@router.callback_query(F.data.startswith("answer_"))
async def check_answer(callback: CallbackQuery, state: FSMContext):
    selected = callback.data.split("_", 1)[1]
    data = await state.get_data()
    mode = await state.get_data()
    correct = data.get("correct")
    points = data.get("points", 0)
    count = data.get("count", 0)
    if selected == correct:
        result = "✅ Правильно!\n\n"
        points += 1
    else:
        result= f"❌ Неправильно. Правильна відповідь: {correct}\n\n"
    count +=1
    level = (await state.get_data()).get("level", "A1")
    word, correct_answer, keyboard = kb.generate_question(level, mode)
    await state.update_data(correct=correct_answer, points=points, count=count)
    await callback.message.edit_text(f"{result}🔤 Як перекладається слово: {word}?", reply_markup=keyboard)

@router.message(F.text == "Завершити тестування")
async def finish_test(message: Message, state: FSMContext, bot: Bot):
    current_state = await state.get_state()
    if current_state != QuizState.testing.state:
        await message.answer("❌ Ви зараз не проходите тестування.")
        return
    data = await state.get_data()
    points = data.get("points", 0)
    count = data.get("count", 0)
    msg_ids = [data.get("select_mode_msg_id"), data.get("test_started_msg_id"), data.get("test_question_msg_id")]

    for msg_id in msg_ids:
        if msg_id:
            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception as e:
                print(f"Не видаляється: {e}")

    await state.clear()
    await message.answer(f"Тестування завершено. Кількість правильних відповідей {points}/{count}", reply_markup=kb.main)

#@router.message(F.text == '💬 Вікторина')
#async def start_test(message: Message):
#    await message.answer("Виберіть режим перекладу:", reply_markup=kb.language)
