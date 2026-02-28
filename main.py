# main.py
import telebot
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------- НАСТРОЙКИ ----------
# Токен берётся из переменной окружения (на Bothost)
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    print("❌ ОШИБКА: токен не найден в переменных окружения!")
    exit()

bot = telebot.TeleBot(TOKEN)

# ---------- ЗАГРУЗКА ДАННЫХ ----------
def load_json_data(filename):
    """Загружает данные из JSON-файла из папки data"""
    try:
        file_path = os.path.join('data', filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Загружен {filename}: {len(data)} записей")
        return data
    except FileNotFoundError:
        print(f"❌ Файл {filename} не найден в папке data")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка в файле {filename}: {e}")
        return []

# Загружаем все категории
stances = load_json_data('stances.json')
blocks = load_json_data('blocks.json')
punches = load_json_data('punches.json')
kicks = load_json_data('kicks.json')
kihon_list = load_json_data('kihon.json')
kata_list = load_json_data('kata.json')
tests = load_json_data('tests.json')

# ---------- КЛАВИАТУРЫ ----------
def create_main_menu_keyboard():
    """Главное меню"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("🥋 Стойки", callback_data='menu_stances'),
        InlineKeyboardButton("🛡️ Блоки", callback_data='menu_blocks'),
        InlineKeyboardButton("👊 Удары руками", callback_data='menu_punches'),
        InlineKeyboardButton("🦵 Удары ногами", callback_data='menu_kicks'),
        InlineKeyboardButton("📚 Кихон", callback_data='menu_kihon'),
        InlineKeyboardButton("📜 Ката", callback_data='menu_kata'),
        InlineKeyboardButton("📝 Тест", callback_data='menu_tests')
    ]
    keyboard.add(*buttons)
    return keyboard

def create_category_keyboard(items):
    """Клавиатура для списка техник в категории"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    for item in items:
        button = InlineKeyboardButton(
            item['name'],
            callback_data=f"show_{item['id']}"
        )
        keyboard.add(button)
    # Кнопка возврата в главное меню
    keyboard.add(InlineKeyboardButton("« Назад", callback_data="main_menu"))
    return keyboard

# ---------- ФУНКЦИЯ ПОИСКА ПО НАЗВАНИЯМ (УРОВЕНЬ 1) ----------
def search_technique_by_name(query):
    """Ищет технику по названию во всех категориях"""
    query_lower = query.lower()
    all_techniques = stances + blocks + punches + kicks + kihon_list + kata_list
    results = []
    for tech in all_techniques:
        # Если название техники целиком содержится в запросе
        if tech['name'].lower() in query_lower:
            results.append(tech)
        else:
            # Ищем отдельные слова запроса в названии
            words = query_lower.split()
            for word in words:
                if len(word) >= 3 and word in tech['name'].lower():
                    results.append(tech)
                    break
    # Убираем дубликаты (если техника попала несколько раз)
    unique = []
    seen_ids = set()
    for tech in results:
        if tech['id'] not in seen_ids:
            unique.append(tech)
            seen_ids.add(tech['id'])
    return unique

# ---------- ФУНКЦИЯ ОТПРАВКИ ИНФОРМАЦИИ О ТЕХНИКЕ ----------
def send_technique_info(chat_id, technique):
    """Отправляет описание техники и ссылку на видео с RuTube"""
    desc = f"*{technique['name']}*\n\n{technique.get('description', '')}"
    bot.send_message(chat_id, desc, parse_mode='Markdown')
    if 'rutube_url' in technique:
        bot.send_message(
            chat_id,
            f"🎥 [Смотреть видео]({technique['rutube_url']})",
            parse_mode='Markdown',
            disable_web_page_preview=False  # чтобы Telegram показывал превью
        )
    else:
        bot.send_message(chat_id, "⚠️ Видео временно недоступно")

# ---------- ФУНКЦИЯ ОТПРАВКИ ТЕСТОВ ----------
def send_test_question(chat_id, test_index):
    """Отправляет вопрос теста с GIF и вариантами ответов"""
    if test_index >= len(tests):
        bot.send_message(
            chat_id,
            "🎉 Тест завершён! Молодец!",
            reply_markup=create_main_menu_keyboard()
        )
        return
    test = tests[test_index]
    keyboard = InlineKeyboardMarkup(row_width=1)
    for opt in test['options']:
        keyboard.add(InlineKeyboardButton(
            opt,
            callback_data=f"test_answer|{test_index}|{opt}"
        ))
    keyboard.add(InlineKeyboardButton("« В меню", callback_data="main_menu"))
    bot.send_animation(
        chat_id,
        test['gif_url'],
        caption=f"❓ {test['question']}",
        reply_markup=keyboard
    )

# ---------- ОБРАБОТЧИК КОМАНДЫ /start ----------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в бот для каратистов!\n"
        "Я помогу подготовиться к аттестации.\n"
        "Выберите раздел в меню ниже:",
        reply_markup=create_main_menu_keyboard()
    )

# ---------- ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ ----------
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.lower()

    # 1. Пытаемся найти технику по названию
    found = search_technique_by_name(text)
    if found:
        if len(found) == 1:
            # Одна техника – показываем сразу
            send_technique_info(message.chat.id, found[0])
            return
        elif len(found) > 1:
            # Несколько – предлагаем выбрать
            kb = InlineKeyboardMarkup(row_width=1)
            for tech in found[:10]:
                kb.add(InlineKeyboardButton(
                    tech['name'],
                    callback_data=f"show_{tech['id']}"
                ))
            kb.add(InlineKeyboardButton("« Главное меню", callback_data="main_menu"))
            bot.send_message(
                message.chat.id,
                "🔍 Нашёл несколько подходящих техник. Уточните:",
                reply_markup=kb
            )
            return

    # 2. Если поиск не дал результатов, проверяем ключевые слова категорий
    if any(w in text for w in ["стойк", "стойка", "дзенкуцу", "киба", "кокуцу"]):
        bot.send_message(
            message.chat.id,
            "🥋 Выберите стойку:",
            reply_markup=create_category_keyboard(stances)
        )
    elif any(w in text for w in ["блок", "уке", "гедан", "учи", "сото", "шуто"]):
        bot.send_message(
            message.chat.id,
            "🛡️ Выберите блок:",
            reply_markup=create_category_keyboard(blocks)
        )
    elif any(w in text for w in ["удар рукой", "цуки", "ой", "гьяку"]):
        bot.send_message(
            message.chat.id,
            "👊 Выберите удар рукой:",
            reply_markup=create_category_keyboard(punches)
        )
    elif any(w in text for w in ["удар ногой", "гери", "мае", "маваши", "йоко", "урамаваши"]):
        bot.send_message(
            message.chat.id,
            "🦵 Выберите удар ногой:",
            reply_markup=create_category_keyboard(kicks)
        )
    elif any(w in text for w in ["кихон", "связк"]):
        bot.send_message(
            message.chat.id,
            "📚 Выберите связку:",
            reply_markup=create_category_keyboard(kihon_list)
        )
    elif any(w in text for w in ["ката", "хейан"]):
        bot.send_message(
            message.chat.id,
            "📜 Выберите ката:",
            reply_markup=create_category_keyboard(kata_list)
        )
    elif any(w in text for w in ["тест", "экзамен", "проверк"]):
        if tests:
            send_test_question(message.chat.id, 0)
        else:
            bot.send_message(
                message.chat.id,
                "❌ Тесты пока не загружены",
                reply_markup=create_main_menu_keyboard()
            )
    else:
        bot.send_message(
            message.chat.id,
            "🤔 Я не понял ваш запрос. Пожалуйста, воспользуйтесь меню:",
            reply_markup=create_main_menu_keyboard()
        )

# ---------- ОБРАБОТЧИК НАЖАТИЙ НА КНОПКИ ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    data = call.data

    # Главное меню
    if data == "main_menu":
        bot.edit_message_text(
            "Главное меню:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=create_main_menu_keyboard()
        )
        return

    # Меню категорий
    if data.startswith("menu_"):
        cat = data[5:]  # убираем "menu_"
        if cat == "stances":
            bot.edit_message_text(
                "🥋 Выберите стойку:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_category_keyboard(stances)
            )
        elif cat == "blocks":
            bot.edit_message_text(
                "🛡️ Выберите блок:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_category_keyboard(blocks)
            )
        elif cat == "punches":
            bot.edit_message_text(
                "👊 Выберите удар рукой:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_category_keyboard(punches)
            )
        elif cat == "kicks":
            bot.edit_message_text(
                "🦵 Выберите удар ногой:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_category_keyboard(kicks)
            )
        elif cat == "kihon":
            bot.edit_message_text(
                "📚 Выберите связку:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_category_keyboard(kihon_list)
            )
        elif cat == "kata":
            bot.edit_message_text(
                "📜 Выберите ката:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_category_keyboard(kata_list)
            )
        elif cat == "tests":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_test_question(call.message.chat.id, 0)
        return

    # Показ конкретной техники
    if data.startswith("show_"):
        tech_id = data[5:]  # убираем "show_"
        all_tech = stances + blocks + punches + kicks + kihon_list + kata_list
        technique = next((t for t in all_tech if t['id'] == tech_id), None)
        if technique:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_technique_info(call.message.chat.id, technique)

            # Возвращаем меню категории, из которой пришли
            if technique in stances:
                bot.send_message(
                    call.message.chat.id,
                    "🥋 Выберите другую стойку:",
                    reply_markup=create_category_keyboard(stances)
                )
            elif technique in blocks:
                bot.send_message(
                    call.message.chat.id,
                    "🛡️ Выберите другой блок:",
                    reply_markup=create_category_keyboard(blocks)
                )
            elif technique in punches:
                bot.send_message(
                    call.message.chat.id,
                    "👊 Выберите другой удар рукой:",
                    reply_markup=create_category_keyboard(punches)
                )
            elif technique in kicks:
                bot.send_message(
                    call.message.chat.id,
                    "🦵 Выберите другой удар ногой:",
                    reply_markup=create_category_keyboard(kicks)
                )
            elif technique in kihon_list:
                bot.send_message(
                    call.message.chat.id,
                    "📚 Выберите другую связку:",
                    reply_markup=create_category_keyboard(kihon_list)
                )
            elif technique in kata_list:
                bot.send_message(
                    call.message.chat.id,
                    "📜 Выберите другое ката:",
                    reply_markup=create_category_keyboard(kata_list)
                )
            else:
                bot.send_message(
                    call.message.chat.id,
                    "Главное меню:",
                    reply_markup=create_main_menu_keyboard()
                )
        else:
            bot.answer_callback_query(call.id, "❌ Информация не найдена")
        return

    # Обработка ответов на тесты
    if data.startswith("test_answer"):
        _, idx_str, ans = data.split('|', 2)
        idx = int(idx_str)
        test = tests[idx]
        if ans == test['correct_answer']:
            bot.answer_callback_query(call.id, "✅ Верно!")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_test_question(call.message.chat.id, idx + 1)
        else:
            bot.answer_callback_query(
                call.id,
                f"❌ Неверно. Правильный ответ: {test['correct_answer']}",
                show_alert=True
            )
        return

# ---------- ЗАПУСК БОТА ----------
if __name__ == "__main__":
    print("🤖 Бот запущен и готов к работе...")
    bot.infinity_polling()