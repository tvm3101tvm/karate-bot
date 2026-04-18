import logging
import random
import sys
import re
import time
from collections import defaultdict
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from aiohttp import ClientTimeout

from config import BOT_TOKEN
from database import (
    get_techniques_by_category, get_technique_by_id, update_progress,
    Session, Technique, UserProgress
)
from keyboards import main_menu, test_options, technique_keyboard, techniques_menu, kihon_submenu
from utils import get_next_test_technique, get_recommendations

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, timeout=ClientTimeout(total=120))
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

user_test_state = {}
# Словарь для защиты от повторных нажатий на кнопки озвучки
last_callback_time = defaultdict(float)
# Хранилище ID последнего голосового сообщения для каждого пользователя
last_voice_message_id = {}

# ---------------------------------------------------------
# Вспомогательная функция отправки вопроса теста
# ---------------------------------------------------------
async def send_question(user_id, tech_id, question_num, total_questions):
    tech = get_technique_by_id(tech_id)
    await bot.send_animation(
        user_id,
        tech.gif_path,
        caption=f'❓ Вопрос {question_num} из {total_questions}\nКак называется эта техника?'
    )
    session = Session()
    all_techs = session.query(Technique).all()
    session.close()
    await bot.send_message(
        user_id,
        'Выберите правильный вариант:',
        reply_markup=test_options(tech, all_techs)
    )

# ---------------------------------------------------------
# КОМАНДЫ
# ---------------------------------------------------------
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(
        'Выберите раздел:',
        reply_markup=main_menu()
    )

@dp.message_handler(commands=['menu'])
async def cmd_menu(message: types.Message):
    await message.answer(
        'Главное меню:',
        reply_markup=main_menu()
    )

@dp.message_handler(commands=['recommend'])
async def cmd_recommend(message: types.Message):
    user_id = message.from_user.id
    recs = get_recommendations(user_id)
    if recs:
        text = 'Рекомендую повторить:\n' + '\n'.join([f'- {t.name_ja} ({t.name_ru})' for t in recs])
    else:
        text = 'Пока нет статистики. Пройдите тест, чтобы получить рекомендации.'
    await message.answer(text, reply_markup=main_menu())

@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    help_text = (
        "📚 <b>Помощь по боту для изучения каратэ</b>\n\n"
        "Этот бот поможет вам изучить базовые техники каратэ и подготовиться к аттестации.\n\n"
        "<b>Основные возможности:</b>\n"
        "• Обучение с помощью GIF-анимации и видео.\n"
        "• Тест из 10 вопросов с выбором правильного названия техники.\n"
        "• Персональные рекомендации на основе ваших ошибок.\n"
        "• <b>Статистика</b>: команда /stats показывает, сколько раз вы отвечали на каждую технику и сколько правильных ответов.\n"
        "• Поиск по названию: просто напишите название техники (например, \"мае-гери\" или \"дзенкуцу дачи\").\n\n"
        "<b>Как пользоваться:</b>\n"
        "– Нажмите кнопку «Меню» (☰) и выберите нужный раздел.\n"
        "– В разделе вы увидите список доступных техник.\n"
        "– Выберите технику – появится её GIF и кнопки «Смотреть видео», «Озвучить» и «Назад в список».\n"
        "– Нажмите «Смотреть видео» – под видео появится кнопка «Назад в список».\n"
        "– Нажмите «Назад в список» чтобы вернуться к выбору.\n"
        "– Для запуска теста нажмите «Тест» в главном меню.\n"
        "– Рекомендации появятся после нескольких тестов.\n\n"
        "Если у вас есть вопросы или предложения, пишите: @KarateForBeginnersHelp"
    )
    await message.reply(help_text, parse_mode="HTML")

@dp.message_handler(commands=['stats'])
async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    session = Session()
    stats = session.query(UserProgress).filter_by(user_id=user_id).all()
    if not stats:
        await message.reply("Статистика пока пуста. Пройдите тест.")
    else:
        text = "Ваша статистика:\n"
        for s in stats:
            tech = session.get(Technique, s.technique_id)
            tech_name = tech.name_ja if tech else str(s.technique_id)
            text += f"{tech_name}: {s.correct_attempts} из {s.total_attempts} правильно\n"
        await message.reply(text)
    session.close()

# ---------------------------------------------------------
# ВРЕМЕННЫЙ ОБРАБОТЧИК ДЛЯ ПОЛУЧЕНИЯ FILE_ID (можно удалить после использования)
# ---------------------------------------------------------
@dp.message_handler(content_types=['photo', 'video', 'animation', 'voice', 'audio'])
async def get_file_id_handler(message: types.Message):
    print(f"Получено медиа типа {message.content_type}")
    file_id = None
    file_type = ""
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "фото"
    elif message.video:
        file_id = message.video.file_id
        file_type = "видео"
    elif message.animation:
        file_id = message.animation.file_id
        file_type = "GIF"
    elif message.voice:
        file_id = message.voice.file_id
        file_type = "голосовое"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "аудио"
    else:
        return
    await message.reply(f"✅ {file_type} file_id:\n`{file_id}`")
    print(f"Отправлен file_id для {file_type}")

# ---------------------------------------------------------
# НАВИГАЦИЯ И ПРОСМОТР ТЕХНИК
# ---------------------------------------------------------
@dp.callback_query_handler(lambda c: c.data == 'main_menu')
async def callback_main_menu(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    message = callback_query.message
    await bot.edit_message_text(
        'Главное меню:',
        chat_id=user_id,
        message_id=message.message_id,
        reply_markup=main_menu()
    )

# --- НОВЫЙ ОБРАБОТЧИК ДЛЯ КНОПКИ «КИХОН» ---
@dp.callback_query_handler(lambda c: c.data == 'kihon')
async def callback_kihon_main(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    await bot.edit_message_text(
        "Выберите категорию:",
        chat_id=user_id,
        message_id=message_id,
        reply_markup=kihon_submenu()
    )

# --- ОБРАБОТЧИК ДЛЯ ВЫБОРА КАТЕГОРИИ ВНУТРИ «КИХОН» ---
@dp.callback_query_handler(lambda c: c.data.startswith('kihon_'))
async def callback_kihon_category(callback_query: types.CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id

    category_map = {
        'kihon_stance': 'stance',
        'kihon_block': 'block',
        'kihon_punch': 'punch',
        'kihon_kick': 'kick'
    }
    if data not in category_map:
        await bot.answer_callback_query(callback_query.id, text="Раздел в разработке", show_alert=False)
        return

    cat = category_map[data]
    # Получаем список техник для выбранной категории
    techniques = get_techniques_by_category(cat)

    # Отображаем список техник (используем существующую функцию techniques_menu)
    await bot.edit_message_text(
        f"Выберите технику из раздела «{category_map_to_name(cat)}»:",
        chat_id=user_id,
        message_id=message_id,
        reply_markup=techniques_menu(cat, techniques)
    )

# --- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ПРЕОБРАЗОВАНИЯ КАТЕГОРИИ В РУССКОЕ НАЗВАНИЕ ---
def category_map_to_name(category):
    names = {
        'stance': 'Стойки',
        'block': 'Блоки',
        'punch': 'Удары руками',
        'kick': 'Удары ногами'
    }
    return names.get(category, 'Техники')

# --- ОБРАБОТЧИК ДЛЯ КНОПКИ «КАТА» (в разработке) ---
@dp.callback_query_handler(lambda c: c.data == 'cat_kata')
async def callback_kata(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    message = callback_query.message
    await bot.send_message(
        user_id,
        "Раздел «Ката» находится в разработке. Следите за обновлениями!",
        reply_markup=main_menu()
    )
    await bot.delete_message(user_id, message.message_id)

# --- ОБРАБОТЧИК ВЫБОРА КОНКРЕТНОЙ ТЕХНИКИ (tech_) ---
@dp.callback_query_handler(lambda c: c.data.startswith('tech_'))
async def callback_tech(callback_query: types.CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
    message = callback_query.message
    tech_id = int(data.split('_')[1])
    tech = get_technique_by_id(tech_id)

    await bot.send_animation(
        user_id,
        tech.gif_path,
        caption=f'{tech.name_ja} ({tech.name_ru})\n{tech.description}',
        reply_markup=technique_keyboard(tech.id)
    )
    await bot.delete_message(user_id, message.message_id)

# --- ОБРАБОТЧИК КНОПКИ «НАЗАД В СПИСОК» (после просмотра техники) ---
@dp.callback_query_handler(lambda c: c.data.startswith('back_to_list_'))
async def callback_back_to_list(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    tech_id = int(callback_query.data.split('_')[3])
    tech = get_technique_by_id(tech_id)
    category = tech.category
    techniques = get_techniques_by_category(category)

    category_title = category_map_to_name(category)
    await bot.send_message(
        user_id,
        f"Выберите технику из раздела «{category_title}»:",
        reply_markup=techniques_menu(category, techniques)
    )

# --- ОБРАБОТЧИК ПРОСМОТРА ВИДЕО ---
@dp.callback_query_handler(lambda c: c.data.startswith('video_'))
async def callback_video(callback_query: types.CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
    tech_id = int(data.split('_')[1])
    tech = get_technique_by_id(tech_id)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton('⬅️ Назад в список', callback_data=f'back_to_list_{tech_id}'))

    await bot.send_video(
        user_id,
        tech.video_path,
        caption=tech.name_ja,
        reply_markup=kb,
        supports_streaming=True
    )

# ---------------------------------------------------------
# ОЗВУЧИВАНИЕ НАЗВАНИЯ ТЕХНИКИ (основной интерфейс)
# ---------------------------------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith('audio_') and not c.data.startswith('audio_feedback_'))
async def callback_audio(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    callback_data = callback_query.data
    now = time.time()

    # Удаляем предыдущее голосовое сообщение пользователя (если есть)
    if user_id in last_voice_message_id:
        try:
            await bot.delete_message(user_id, last_voice_message_id[user_id])
        except Exception:
            pass

    key = f"{user_id}_{callback_data}"
    if now - last_callback_time[key] < 3:
        await bot.answer_callback_query(callback_query.id, text="Подождите...", show_alert=False)
        return
    last_callback_time[key] = now

    await bot.answer_callback_query(callback_query.id, cache_time=5)

    tech_id = int(callback_data.split('_')[1])
    tech = get_technique_by_id(tech_id)

    if tech.audio_path:
        msg = await callback_query.message.reply_voice(
            tech.audio_path,
            caption=f"Произношение: {tech.name_ja}"
        )
        last_voice_message_id[user_id] = msg.message_id
    else:
        await callback_query.message.reply("Аудио пока не добавлено")

# ---------------------------------------------------------
# ОЗВУЧИВАНИЕ НАЗВАНИЯ ТЕХНИКИ ПОСЛЕ ОТВЕТА В ТЕСТЕ
# ---------------------------------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith('audio_feedback_'))
async def callback_audio_feedback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    callback_data = callback_query.data
    now = time.time()

    if user_id in last_voice_message_id:
        try:
            await bot.delete_message(user_id, last_voice_message_id[user_id])
        except Exception:
            pass

    key = f"{user_id}_{callback_data}"
    if now - last_callback_time[key] < 3:
        await bot.answer_callback_query(callback_query.id, text="Подождите...", show_alert=False)
        return
    last_callback_time[key] = now

    await bot.answer_callback_query(callback_query.id, cache_time=5)

    tech_id = int(callback_data.split('_')[2])
    tech = get_technique_by_id(tech_id)

    if tech.audio_path:
        msg = await callback_query.message.reply_voice(
            tech.audio_path,
            caption=f"Произношение: {tech.name_ja}"
        )
        last_voice_message_id[user_id] = msg.message_id
    else:
        await callback_query.message.reply("Аудио пока не добавлено")

# ---------------------------------------------------------
# ТЕСТИРОВАНИЕ
# ---------------------------------------------------------
@dp.callback_query_handler(lambda c: c.data == 'test_start')
async def callback_test_start(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    total_questions = 10

    questions_ids = []
    max_attempts = 100
    attempts = 0
    while len(questions_ids) < total_questions and attempts < max_attempts:
        tech = get_next_test_technique(user_id)
        if tech.id not in questions_ids:
            questions_ids.append(tech.id)
        attempts += 1

    if len(questions_ids) < total_questions:
        session = Session()
        all_ids = [t.id for t in session.query(Technique.id).all()]
        session.close()
        remaining = total_questions - len(questions_ids)
        possible = [i for i in all_ids if i not in questions_ids]
        if possible:
            questions_ids.extend(random.sample(possible, min(remaining, len(possible))))

    user_test_state[user_id] = {
        'questions': questions_ids,
        'current': 0,
        'correct_count': 0,
        'total': len(questions_ids)
    }

    await send_question(user_id, questions_ids[0], 1, len(questions_ids))
    await bot.delete_message(user_id, callback_query.message.message_id)

@dp.callback_query_handler(lambda c: c.data.startswith('test_answer'))
async def callback_test_answer(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    parts = data.split('_')
    correct_id = int(parts[2])
    chosen_id = int(parts[3])

    state = user_test_state.get(user_id)
    if not state:
        await bot.send_message(user_id, "❌ Тест не найден. Начните заново.", reply_markup=main_menu())
        await bot.delete_message(user_id, callback_query.message.message_id)
        return

    current_index = state['current']
    questions = state['questions']
    if current_index >= len(questions):
        await bot.send_message(user_id, "⚠️ Тест уже завершён.", reply_markup=main_menu())
        user_test_state.pop(user_id, None)
        await bot.delete_message(user_id, callback_query.message.message_id)
        return

    current_tech_id = questions[current_index]
    if correct_id != current_tech_id:
        await bot.send_message(user_id, "⚠️ Ошибка теста. Начните заново.", reply_markup=main_menu())
        user_test_state.pop(user_id, None)
        await bot.delete_message(user_id, callback_query.message.message_id)
        return

    tech = get_technique_by_id(correct_id)

    if chosen_id == correct_id:
        state['correct_count'] += 1
        feedback = f"✅ Правильно! Это {tech.name_ja} ({tech.name_ru})"
    else:
        feedback = f"❌ Неправильно. Правильный ответ: {tech.name_ja} ({tech.name_ru})"

    is_last = (state['current'] + 1) >= len(questions)

    kb = InlineKeyboardMarkup(row_width=1)
    if not is_last:
        kb.add(
            InlineKeyboardButton('🔊 Озвучить название', callback_data=f'audio_feedback_{correct_id}'),
            InlineKeyboardButton('Следующий вопрос ➡️', callback_data='next_question')
        )
    else:
        kb.add(InlineKeyboardButton('🔊 Озвучить название', callback_data=f'audio_feedback_{correct_id}'))

    try:
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            text=feedback,
            reply_markup=kb
        )
    except Exception as e:
        print(f"Ошибка редактирования сообщения: {e}")
        await bot.send_message(user_id, feedback, reply_markup=kb)

    update_progress(user_id, correct_id, chosen_id == correct_id)

    state['current'] += 1

    if is_last:
        total = len(questions)
        correct = state['correct_count']
        await bot.send_message(
            user_id,
            f"🎉 Тест завершён! Правильных ответов: {correct} из {total}."
        )
        await bot.send_message(
            user_id,
            "Что дальше?",
            reply_markup=main_menu()
        )
        user_test_state.pop(user_id, None)

@dp.callback_query_handler(lambda c: c.data == 'next_question')
async def callback_next_question(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    message = callback_query.message

    state = user_test_state.get(user_id)
    if not state:
        await bot.send_message(user_id, "❌ Тест не найден. Начните заново.", reply_markup=main_menu())
        return

    current_index = state['current']
    questions = state['questions']
    if current_index >= len(questions):
        total = len(questions)
        correct = state['correct_count']
        await bot.send_message(
            user_id,
            f"🎉 Тест завершён! Правильных ответов: {correct} из {total}."
        )
        await bot.send_message(
            user_id,
            "Что дальше?",
            reply_markup=main_menu()
        )
        user_test_state.pop(user_id, None)
        return

    next_tech_id = questions[current_index]
    await send_question(user_id, next_tech_id, current_index + 1, len(questions))

@dp.callback_query_handler(lambda c: c.data == 'test_cancel')
async def callback_test_cancel(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    try:
        await bot.delete_message(user_id, callback_query.message.message_id)
    except Exception:
        pass
    user_test_state.pop(user_id, None)
    await bot.send_message(
        user_id,
        "✅ Тест прерван. Возвращаюсь в главное меню.",
        reply_markup=main_menu()
    )

# ---------------------------------------------------------
# РЕКОМЕНДАЦИИ
# ---------------------------------------------------------
@dp.callback_query_handler(lambda c: c.data == 'recommend')
async def callback_recommend(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    recs = get_recommendations(user_id)
    if recs:
        text = 'Рекомендую повторить:\n' + '\n'.join([f'- {t.name_ja} ({t.name_ru})' for t in recs])
    else:
        text = 'Пока нет статистики. Пройдите тест, чтобы получить рекомендации.'
    await bot.send_message(user_id, text, reply_markup=main_menu())

# ---------------------------------------------------------
# ТЕКСТОВЫЙ ПОИСК
# ---------------------------------------------------------
@dp.message_handler()
async def handle_text(message: types.Message):
    raw_text = message.text.lower().strip()
    print(f"DEBUG: пользователь ввёл текст: '{raw_text}'")

    def normalize(s: str) -> str:
        s = re.sub(r'[^\w\s]', '', s)
        return s.replace(' ', '').lower()

    normalized_query = normalize(raw_text)

    session = Session()
    all_techs = session.query(Technique).all()
    session.close()

    tech = next(
        (t for t in all_techs
         if normalized_query in normalize(t.name_ru)
         or normalized_query in normalize(t.name_ja)),
        None
    )

    if tech:
        print(f"DEBUG: НАЙДЕНО! {tech.name_ru} | {tech.name_ja}")
        await message.reply_animation(
            tech.gif_path,
            caption=f'{tech.name_ja} ({tech.name_ru})\n{tech.description}',
            reply_markup=technique_keyboard(tech.id)
        )
        category = tech.category
        category_title = category_map_to_name(category)
        techniques = get_techniques_by_category(category)
        await bot.send_message(
            message.chat.id,
            f"Выберите технику из раздела «{category_title}»:",
            reply_markup=techniques_menu(category, techniques)
        )
    else:
        print("DEBUG: НИЧЕГО НЕ НАЙДЕНО")
        await message.reply(
            'Я не понял запрос. Пожалуйста, воспользуйтесь меню.',
            reply_markup=main_menu()
        )

# ---------------------------------------------------------
# СЛУЖЕБНЫЕ ФУНКЦИИ И ЗАПУСК
# ---------------------------------------------------------
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="recommend", description="Рекомендации"),
        BotCommand(command="stats", description="Моя статистика"),
        BotCommand(command="help", description="Помощь"),
    ]
    await bot.set_my_commands(commands)

async def on_startup(dp):
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)
    session = Session()
    tech_count = session.query(Technique).count()
    print(f"=== DATABASE CHECK: {tech_count} techniques found ===")
    session.close()
    print("Вебхук сброшен, ожидающие обновления удалены, команды меню установлены")

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True, timeout=60)