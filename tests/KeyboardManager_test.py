#! /usr/bin/env python
# -*- coding: utf-8 -*-

from managers.KeyboardManager import return_keyboard, generate_categories_kb, generate_user_recipes_kb


def test_kb_generator():
    first_choice_keyboard = return_keyboard('first_choice_keyboard')
    searchable_keyboard = return_keyboard('searchable_keyboard')
    final_choice_keyboard = return_keyboard('final_choice_keyboard')

    print("Клавиатуры в формате списков")
    print(first_choice_keyboard)
    print(searchable_keyboard)
    print(final_choice_keyboard)

    first_choice_keyboard_txt = return_keyboard('first_choice_keyboard', True)
    searchable_keyboard_txt = return_keyboard('searchable_keyboard', True)
    final_choice_keyboard_txt = return_keyboard('final_choice_keyboard', True)

    print("Клавиатуры в формате строк")
    print(first_choice_keyboard_txt)
    print(searchable_keyboard_txt)
    print(final_choice_keyboard_txt)

    print('\n')


def test_categories_generator():
    print("Клавиатуры категорий")
    print(generate_categories_kb())
    print('\n')


def test_generate_user_recipes_kb():
    print("Inline клаиатура с рецептами пользоваля 99760649 и категорией = 1")
    print(generate_user_recipes_kb(99760649, 1))
    print('\n')


test_kb_generator()
test_categories_generator()
test_generate_user_recipes_kb()
