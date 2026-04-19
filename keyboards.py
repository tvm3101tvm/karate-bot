from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    """Главное меню: Кихон, Ката, Тест, Рекомендации"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton('Кихон', callback_data='kihon'),
        InlineKeyboardButton('Ката', callback_data='cat_kata'),
        InlineKeyboardButton('Тест', callback_data='test_start'),
        InlineKeyboardButton('Рекомендации', callback_data='recommend')
    )
    return kb

def kihon_submenu():
    """Подменю для раздела Кихон (выбор категории)"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton('Стойки', callback_data='kihon_stance'),
        InlineKeyboardButton('Блоки', callback_data='kihon_block'),
        InlineKeyboardButton('Удары руками', callback_data='kihon_punch'),
        InlineKeyboardButton('Удары ногами', callback_data='kihon_kick')
    )
    kb.add(InlineKeyboardButton('Назад', callback_data='main_menu'))
    return kb

def techniques_menu(category, techniques):
    """Меню выбора техники из категории (вертикальные кнопки)"""
    kb = InlineKeyboardMarkup(row_width=1)
    for tech in techniques:
        button_text = f"{tech.name_ja} ({tech.name_ru})"
        kb.insert(InlineKeyboardButton(button_text, callback_data=f'tech_{tech.id}'))
    # Кнопка "Назад" возвращает в подменю Кихон
    kb.add(InlineKeyboardButton('Назад', callback_data='back_to_kihon_submenu'))
    return kb

def technique_keyboard(tech_id):
    """Клавиатура для одной техники: видео, аудио, назад в список"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton('🔊 Озвучить', callback_data=f'audio_{tech_id}'),
        InlineKeyboardButton('Смотреть видео', callback_data=f'video_{tech_id}')
    )
    kb.add(InlineKeyboardButton('⬅️ Назад в список', callback_data=f'back_to_list_{tech_id}'))
    return kb

def test_options(tech, all_techs):
    """Клавиатура для теста: варианты ответов и кнопка прерывания"""
    import random
    options = [tech]
    others = [t for t in all_techs if t.id != tech.id]
    random.shuffle(others)
    options.extend(others[:3])
    random.shuffle(options)
    kb = InlineKeyboardMarkup(row_width=2)
    for opt in options:
        kb.insert(InlineKeyboardButton(opt.name_ja, callback_data=f'test_answer_{tech.id}_{opt.id}'))
    kb.add(InlineKeyboardButton('❌ Прервать тест', callback_data='test_cancel'))
    return kb