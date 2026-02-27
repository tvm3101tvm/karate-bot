# main.py
import telebot
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ============= НАСТРОЙКИ =============
# Токен будет браться из переменных окружения (на Bothost)
TOKEN = os.environ.get('BOT_TOKEN')

if not TOKEN:
    print("❌ ОШИБКА: Токен не найден в переменных окружения!")
    exit()

print(f"✅ Токен загружен")

bot = telebot.TeleBot(TOKEN)

# ============= ЗАГРУЗКА ДАННЫХ =============

def load_json_data(filename):
    """Загружает данные из JSON-файла"""
    try:
        file_path = os.path.join('data', filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Загружен {filename}: {len(data)} записей")
        return data
    except FileNotFoundError:
        print(f"❌ Файл {filename} не найден")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка в файле {filename}: {e}")
        return []

# Загружаем все данные
stances = load_json_data('stances.json')
blocks = load_json_data('blocks.json')
punches = load_json_data('punches.json')
kicks = load_json_data('kicks.json')
kihon_list = load_json_data('kihon.json')
kata_list = load_json_data('kata.json')
tests = load_json_data('tests.json')

# ============= КЛАВИАТУРЫ =============

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
    """Клавиатура для списка техник"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    for item in items:
        button = InlineKeyboardButton(
            item['name'], 
            callback_data=f"show_{item['id']}"
        )
        keyboard.add(button)
    
    keyboard.add(InlineKeyboardButton(
        "« Назад", 
        callback_data="main_menu"
    ))
    return keyboard

# ============= ПОИСК ТЕХНИКИ =============

def find_technique_by_id(technique_id):
    """Ищет технику по ID во всех категориях"""
    all_techniques = stances + blocks + punches + kicks + kihon_list + kata_list
    for item in all_techniques:
        if item['id'] == technique_id:
            return item
    return None

# ============= ОТПРАВКА ВИДЕО =============

def send_technique_info(chat_id, technique):
    """Отправляет информацию о технике с видео через RuTube"""
    
    # Отправляем описание
    desc_text = f"*{technique['name']}*\n\n{technique.get('description', '')}"
    bot.send_message(chat_id, desc_text, parse_mode='Markdown')
    
    # Отправляем ссылку на видео
    if 'rutube_url' in technique:
        video_text = f"🎥 [Смотреть видео]({technique['rutube_url']})"
        bot.send_message(
            chat_id,
            video_text,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
    else:
        bot.send_message(chat_id, "⚠️ Видео временно недоступно")

# ============= ТЕСТЫ =============

def send_test_question(chat_id, test_index):
    """Отправляет вопрос теста"""
    if test_index >= len(tests):
        bot.send_message(
            chat_id, 
            "🎉 Тест завершен! Молодец!",
            reply_markup=create_main_menu_keyboard()
        )
        return
    
    test = tests[test_index]
    
    # Создаем клавиатуру с вариантами
    keyboard = InlineKeyboardMarkup(row_width=1)
    for option in test['options']:
        keyboard.add(InlineKeyboardButton(
            option, 
            callback_data=f"test_answer|{test_index}|{option}"
        ))
    
    keyboard.add(InlineKeyboardButton(
        "« В меню", 
        callback_data="main_menu"
    ))
    
    # Отправляем GIF (если есть ссылка)
    if 'gif_url' in test:
        bot.send_animation(
            chat_id,
            test['gif_url'],
            caption=f"❓ {test['question']}",
            reply_markup=keyboard
        )
    else:
        bot.send_message(
            chat_id,
            f"❓ {test['question']}",
            reply_markup=keyboard
        )

# ============= ОБРАБОТЧИКИ =============

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 Добро пожаловать в бот для каратистов!\n\n"
        "Я помогу подготовиться к аттестации.\n"
        "Выбери раздел в меню ниже:"
    )
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        reply_markup=create_main_menu_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Обработчик нажатий на кнопки"""
    
    # Главное меню
    if call.data == "main_menu":
        bot.edit_message_text(
            "Главное меню:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=create_main_menu_keyboard()
        )
        return
    
    # Меню категорий
    if call.data.startswith("menu_"):
        category = call.data[5:]
        
        if category == "stances" and stances:
            bot.edit_message_text(
                "🥋 Выберите стойку:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_category_keyboard(stances)
            )
        elif category == "blocks" and blocks:
            bot.edit_message_text(
                "🛡️ Выберите блок:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_category_keyboard(blocks)
            )
        elif category == "punches" and punches:
            bot.edit_message_text(
                "👊 Выберите удар:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_category_keyboard(punches)
            )
        elif category == "kicks" and kicks:
            bot.edit_message_text(
                "🦵 Выберите удар:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_category_keyboard(kicks)
            )
        elif category == "kihon" and kihon_list:
            bot.edit_message_text(
                "📚 Выберите связку:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_category_keyboard(kihon_list)
            )
        elif category == "kata" and kata_list:
            bot.edit_message_text(
                "📜 Выберите ката:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_category_keyboard(kata_list)
            )
        elif category == "tests":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_test_question(call.message.chat.id, 0)
        return
    
    # Показ техники
    if call.data.startswith("show_"):
        technique_id = call.data[5:]
        technique = find_technique_by_id(technique_id)
        
        if technique:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_technique_info(call.message.chat.id, technique)
            
            # Возвращаем меню категории
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
            else:
                bot.send_message(
                    call.message.chat.id,
                    "Главное меню:",
                    reply_markup=create_main_menu_keyboard()
                )
        return
    
    # Обработка ответов на тесты
    if call.data.startswith("test_answer"):
        _, test_index_str, answer = call.data.split('|', 2)
        test_index = int(test_index_str)
        test = tests[test_index]
        
        if answer == test['correct_answer']:
            bot.answer_callback_query(call.id, "✅ Правильно!")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_test_question(call.message.chat.id, test_index + 1)
        else:
            bot.answer_callback_query(
                call.id, 
                f"❌ Неверно. Правильный ответ: {test['correct_answer']}",
                show_alert=True
            )

# ============= ЗАПУСК =============
if __name__ == "__main__":
    print("\n" + "="*40)
    print("🤖 БОТ ЗАПУЩЕН!")
    print("="*40)
    bot.infinity_polling()