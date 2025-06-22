from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton
import json
import random

def load_words_from_json(current_level="A1") -> list[dict]:
    with open("dictionary.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data.get(current_level, [])

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='✏️ Тестування'), KeyboardButton(text='💬 Вікторина')],
    [KeyboardButton(text='💪 Складність'), KeyboardButton(text='❔ Довідка')]
],
    resize_keyboard=True,
    input_field_placeholder='Оберіть дію...')

exit_test = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Завершити тестування')]
],
    resize_keyboard=True,
    input_field_placeholder='Тестування...')

level = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🟢 A1'), KeyboardButton(text='🟢 A2')],
    [KeyboardButton(text='🟡 B1'), KeyboardButton(text='🟡 B2')],
    [KeyboardButton(text='🟠 C1'), KeyboardButton(text='🟠 C2')]
],
    resize_keyboard=True,
    input_field_placeholder='Оберіть складність...')

language = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🇬🇧 ENG→UA', callback_data='eng_to_ua'), InlineKeyboardButton(text='🇺🇦 UA→ENG', callback_data='ua_to_eng')]
])

def get_words(words: list[dict]) -> tuple[str, str, list[str]]:
    correct = random.choice(words)
    other_options = [w["ua"] for w in words if w != correct]
    random.shuffle(other_options)
    incorrect = other_options[:3]

    all_options = incorrect + [correct["ua"]]
    random.shuffle(all_options)

    question_word = correct["en"]
    correct_answer = correct["ua"]

    return question_word, correct_answer, all_options

def build_answer_keyboard(options: list[str]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=opt, callback_data=f"answer_{opt}")]
        for opt in options
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def generate_question(current_level="A1"):
    words = load_words_from_json(current_level)
    question_word, correct_answer, options = get_words(words)
    keyboard = build_answer_keyboard(options)
    return question_word, correct_answer, keyboard
