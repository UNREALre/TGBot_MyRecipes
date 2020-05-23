#! /usr/bin/env python
# -*- coding: utf-8 -*-

from managers.RecipeManager import get_categories, get_user_recipes, find_recipe
from telegram import InlineKeyboardButton


def return_keyboard(kb_name, as_text=False, separator='|'):
    """
    Получает наименование клавиатуры и флаг возвращаемого формата
    Возвращает список кнопок соответствующих списком, либо, если as_text=True - строкой
    """
    keyboard = []
    if kb_name == "first_choice_keyboard":
        keyboard.append(['Добавить рецепт', 'Найти рецепт'])
    elif kb_name == "searchable_keyboard":
        keyboard.append(['Да, разрешить', 'Нет, рецепт приватный'])
    elif kb_name == "final_choice_keyboard":
        keyboard.append(['Да, сохранить рецепт', 'Нет, изменить название'])
        keyboard.append(['Нет, изменить ингредиенты', 'Нет, изменить описание'])
        keyboard.append(['Нет, изменить категорию', 'Нет, изменить приватность'])
    elif kb_name == "back_to_categories":
        keyboard.append(['Выбрать другую категорию'])
    elif kb_name == "back_to_search_keyword":
        keyboard.append(['Изменить поисковый запрос'])

    if as_text:
        kb_txt = []
        for elem in keyboard:
            if type(elem) is list:
                for sub_elem in elem:
                    kb_txt.append(sub_elem)
            else:
                kb_txt.append(elem)

        keyboard = separator.join(kb_txt)

    return keyboard


def generate_categories_kb():
    """
    Возвращает клавиатуру со всеми доступными категориями рецептов в системе
    """
    tags_keyboard = []
    tags = get_categories()
    i = 0
    btn_row = []
    for tag in tags:
        btn_row.append(tag['name'])
        i += 1
        if i % 2 == 0:
            tags_keyboard.append(btn_row)
            btn_row = []

    return tags_keyboard


def generate_user_recipes_kb(user_id, category_id=None, keyword=None):
    """
    Принимает id пользователя, category_id, keyword
    Если keyword передан, то category_id игнорируется, ищем просто по ключевику
    Возвращает inline клавиатуру со списком всех его рецептов, если задана категория - фильтр по ней
    """
    if keyword:
        user_recipes = find_recipe(keyword, user_id)
    else:
        user_recipes = get_user_recipes(user_id, category_id)

    recipes_keyboard = []
    for recipe in user_recipes:
        title = '"' + recipe['title'][:25] + ('..."' if len(recipe['title']) > 25 else '"')
        title += ' от @' + recipe['user_name'] if keyword else ''
        recipes_keyboard.append([InlineKeyboardButton(title, callback_data=str(recipe['_id']))])

    return recipes_keyboard


def generate_like_keyboard(user_id, recipe_id):
    """
    Принимает id пользователя и id рецепта
    Возвращает кнопку для лайка
    """
    cb_value = str(user_id)+"~"+str(recipe_id)
    return [[InlineKeyboardButton('Лайк!', callback_data=cb_value)]]
