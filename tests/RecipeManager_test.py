#! /usr/bin/env python
# -*- coding: utf-8 -*-

from managers.RecipeManager import (get_category_by_id, get_categories,
                                    get_user_recipes, find_recipe_by_id,
                                    find_recipe, format_recipe_for_output)


def test_get_category_by_id():
    print("Получение категории по ID = 1")
    print(get_category_by_id(1))
    print('\n')


def test_get_categories():
    print("Получение списка всех категорий")
    print(get_categories())
    print('\n')


def test_get_user_recipes():
    print("Получение рецептов пользователя с ID = 99760649")
    print(get_user_recipes(99760649))
    print('\n')
    print("Получение рецептов пользователя с ID = 99760649 и Категорий = 2")
    print(get_user_recipes(99760649, 2))
    print('\n')


def test_find_recipe_by_id():
    print("Ищет рецепт с ID = 5ec78efe881a397b0156bdbe")
    print(find_recipe_by_id('5ec78efe881a397b0156bdbe'))
    print('\n')


def test_format_recipe_for_output():
    print("Форматируванный для вывода пользователю рецепт")
    print(format_recipe_for_output(find_recipe_by_id('5ec78efe881a397b0156bdbe')))
    print('\n')


def test_find_recipe():
    print("Поиск рецепта по ключевому слову макароны с пользователем 11760649")
    print(find_recipe('макароны', 11760649))
    print('\n')


# test_get_categories()
# test_get_category_by_id()
# test_get_user_recipes()
# test_find_recipe_by_id()
# test_format_recipe_for_output()
test_find_recipe()