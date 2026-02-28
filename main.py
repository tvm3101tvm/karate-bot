# main.py
import telebot
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------- НАСТРОЙКИ ----------
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    print("❌ ОШИБКА: токен не найден в переменных окружения!")
    exit()

bot = telebot.TeleBot(TOKEN)

# ---------- ЗАГРУЗКА ДАННЫХ ----------
def load_json_data(filename):
    try:
        file_path = os.path.join('data', filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Загружен {filename}: {len(data)} записей")
        return data
    except Exception as e:
        print(f"❌ Ошибка загрузки {filename}: {e}")
        return []

stances = load_json_data('stances.json')
blocks = load_json_data('blocks.json')
punches = load_json_data('punches.json')
kicks = load_json_data('kicks.json')
kihon_list = load_json_data('kihon.json')
kata_list = load_json_data('kata.json')
tests = load_json_data('tests.json')

# ---------- КЛАВИАТУРЫ ----------
def create_main_menu_keyboard():
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

# ---------- ФУНКЦИЯ ПОИСКА ----------
def search_technique_by_name(query):
    query_lower = query.lower()
    all_tech = stances + blocks + punches + kicks + kihon_list + kata_list
    results = []
    for tech in all_tech:
        if tech['name'].lower() in query_lower:
            results.append(tech)
        else:
            words = query_lower.split()
            for word in words:
                if len(word) >= 3 and word in tech['name'].lower():
                    results.append(tech)
                    break
    unique = []
    seen_ids = set()
    for tech in results:
        if tech['id'] not in seen_ids:
            unique.append(tech)
            seen_ids.add(tech['id'])
    return unique

# ---------- ОТПРАВКА ИНФОРМАЦИИ О ТЕХНИКЕ (ПОДРОБНО) ----------
def send_technique_info(chat_id, technique):
    """Отправляет фото (если есть), описание и ссылку на видео"""
    # Фото с названием
    if 'photo_url' in technique and technique['photo_url']:
        try:
            bot.send_photo(
                chat_id,
                technique['photo_url'],
                caption=f"*{technique['name']}*",
                parse_mode='Markdown'
            )
        except:
            bot.send_message(chat_id, f"*{technique['name']}*", parse_mode='Markdown')
    else:
        bot.send_message(chat_id, f"*{technique['name']}*", parse_mode='Markdown')

    # Описание
    if technique.get('description'):
        bot.send_message(chat_id, technique['description'], parse_mode='Markdown')

    # Видео
    if 'rutube_url' in technique:
        bot.send_message(
            chat_id,
            f"🎥 [Смотреть видео]({technique['rutube_url']})",
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
    else:
        bot.send_message(chat_id, "⚠️ Видео временно недоступно")

# ---------- НОВАЯ ФУНКЦИЯ: ПОКАЗ ВСЕХ ЭЛЕМЕНТОВ КАТЕГОРИИ С ФОТО ----------
def send_category_items(chat_id, items, category_name):
    """
    Отправляет все элементы категории с фото (если есть) и кнопкой "Смотреть видео".
    После завершения выводит главное меню.
    """
    for item in items:
        # Формируем клавиатуру с кнопкой на видео
        keyboard = None
        if 'rutube_url' in item:
            keyboard = InlineKeyboardMarkup().add(
                InlineKeyboardButton("🎥 Смотреть видео", url=item['rutube_url'])
            )

        # Отправляем фото или просто название
        caption = f"*{item['name']}*"
        try:
            if 'photo_url' in item and item['photo_url']:
                bot.send_photo(
                    chat_id,
                    item['photo_url'],
                    caption=caption,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
            else:
                bot.send_message(
                    chat_id,
                    caption,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
        except Exception as e:
            print(f"Ошибка при отправке {item['name']}: {e}")
            # Если фото не отправилось, шлём просто текст
            bot.send_message(chat_id, caption, parse_mode='Markdown', reply_markup=keyboard)

    # После всех техник возвращаем главное меню
    bot.send_message(chat_id, "Выберите категорию:", reply_markup=create_main_menu_keyboard())

# ---------- ТЕСТЫ ----------
def send_test_question(chat_id, index):
    if index >= len(tests):
        bot.send_message(chat_id, "🎉 Тест завершён!", reply_markup=create_main_menu_keyboard())
        return
    test = tests[index]
    keyboard = InlineKeyboardMarkup(row_width=1)
    for opt in test['options']:
        keyboard.add(InlineKeyboardButton(opt, callback_data=f"test_answer|{index}|{opt}"))
    keyboard.add(InlineKeyboardButton("« В меню", callback_data="main_menu"))
    bot.send_animation(chat_id, test['gif_url'], caption=f"❓ {test['question']}", reply_markup=keyboard)

# ---------- ОБРАБОТЧИКИ ----------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в бот для каратистов!\n"
        "Я помогу подготовиться к аттестации.\n"
        "Выберите раздел в меню ниже:",
        reply_markup=create_main_menu_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.lower()
    found = search_technique_by_name(text)
    if found:
        if len(found) == 1:
            send_technique_info(message.chat.id, found[0])
            return
        else:
            kb = InlineKeyboardMarkup(row_width=1)
            for tech in found[:10]:
                kb.add(InlineKeyboardButton(tech['name'], callback_data=f"show_{tech['id']}"))
            kb.add(InlineKeyboardButton("« Главное меню", callback_data="main_menu"))
            bot.send_message(message.chat.id, "🔍 Нашёл несколько вариантов:", reply_markup=kb)
            return

    # Ключевые слова категорий (оставлено для обратной совместимости)
    if any(w in text for w in ["стойк", "стойка", "дзенкуцу", "киба", "кокуцу"]):
        bot.send_message(message.chat.id, "🥋 Выберите категорию:", reply_markup=create_main_menu_keyboard())
    elif any(w in text for w in ["блок", "уке", "гедан", "учи", "сото", "шуто"]):
        bot.send_message(message.chat.id, "🛡️ Выберите категорию:", reply_markup=create_main_menu_keyboard())
    elif any(w in text for w in ["удар рукой", "цуки", "ой", "гьяку"]):
        bot.send_message(message.chat.id, "👊 Выберите категорию:", reply_markup=create_main_menu_keyboard())
    elif any(w in text for w in ["удар ногой", "гери", "мае", "маваши", "йоко", "урамаваши"]):
        bot.send_message(message.chat.id, "🦵 Выберите категорию:", reply_markup=create_main_menu_keyboard())
    elif any(w in text for w in ["кихон", "связк"]):
        bot.send_message(message.chat.id, "📚 Выберите категорию:", reply_markup=create_main_menu_keyboard())
    elif any(w in text for w in ["ката", "хейан"]):
        bot.send_message(message.chat.id, "📜 Выберите категорию:", reply_markup=create_main_menu_keyboard())
    elif any(w in text for w in ["тест", "экзамен", "проверк"]):
        if tests:
            send_test_question(message.chat.id, 0)
        else:
            bot.send_message(message.chat.id, "❌ Тесты пока не загружены", reply_markup=create_main_menu_keyboard())
    else:
        bot.send_message(message.chat.id, "🤔 Я не понял. Воспользуйтесь меню:", reply_markup=create_main_menu_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    data = call.data

    if data == "main_menu":
        bot.edit_message_text("Главное меню:", call.message.chat.id, call.message.message_id,
                              reply_markup=create_main_menu_keyboard())
        return

    if data.startswith("menu_"):
        cat = data[5:]
        # Удаляем сообщение с кнопкой категории, чтобы не загромождать чат
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass  # если не удалось удалить, игнорируем

        if cat == "stances" and stances:
            send_category_items(call.message.chat.id, stances, "стойки")
        elif cat == "blocks" and blocks:
            send_category_items(call.message.chat.id, blocks, "блоки")
        elif cat == "punches" and punches:
            send_category_items(call.message.chat.id, punches, "удары руками")
        elif cat == "kicks" and kicks:
            send_category_items(call.message.chat.id, kicks, "удары ногами")
        elif cat == "kihon" and kihon_list:
            send_category_items(call.message.chat.id, kihon_list, "кихон")
        elif cat == "kata" and kata_list:
            send_category_items(call.message.chat.id, kata_list, "ката")
        elif cat == "tests":
            send_test_question(call.message.chat.id, 0)
        else:
            bot.send_message(call.message.chat.id, "❌ Категория пуста", reply_markup=create_main_menu_keyboard())
        return

    if data.startswith("show_"):
        tech_id = data[5:]
        all_tech = stances + blocks + punches + kicks + kihon_list + kata_list
        technique = next((t for t in all_tech if t['id'] == tech_id), None)
        if technique:
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            send_technique_info(call.message.chat.id, technique)
            # Возвращаем главное меню
            bot.send_message(call.message.chat.id, "Главное меню:", reply_markup=create_main_menu_keyboard())
        else:
            bot.answer_callback_query(call.id, "❌ Не найдено")
        return

    if data.startswith("test_answer"):
        _, idx_str, ans = data.split('|', 2)
        idx = int(idx_str)
        test = tests[idx]
        if ans == test['correct_answer']:
            bot.answer_callback_query(call.id, "✅ Верно!")
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            send_test_question(call.message.chat.id, idx + 1)
        else:
            bot.answer_callback_query(call.id, f"❌ Неверно. Правильный ответ: {test['correct_answer']}", show_alert=True)

if __name__ == "__main__":
    print("🤖 Бот запущен и готов к работе...")
    bot.infinity_polling()