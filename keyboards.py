from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='✏️ Тестування'), KeyboardButton(text='💬 Вікторина')],
    [KeyboardButton(text='💪 Складність'), KeyboardButton(text='❔ Довідка')]
],
    resize_keyboard=True,
    input_field_placeholder='Оберіть дію...')

language = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ENG→UA', callback_data='engtoua'), InlineKeyboardButton(text='UA→ENG', callback_data='uatoeng')]
])