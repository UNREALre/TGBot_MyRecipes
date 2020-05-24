#! /usr/bin/env python
# -*- coding: utf-8 -*-

from config import db
from bson.objectid import ObjectId
import re

recipe_collection = db['recipe']
tags_collection = db['tags']


def find_recipe(keyword, user_id):
    """
    Принимает ключевое слово для поиска рецепта, что ввел пользователь и user_id
    Возвращает найденные рецепты у которых стоит флаг доступа для поиска
    Либо все, которые принадлежат текущему пользователю
    """
    recipes = []
    rgx = re.compile(keyword, re.IGNORECASE)

    good_tags = []  # в головном поиске сделаем выборку всех рецептов из данных категорий
    tag_cursor = tags_collection.find(
        {
            'name': rgx,
        },
        {'score': {'$meta': "textScore"}},
    )
    for tag in tag_cursor:
        good_tags.append(tag['tag_id'])

    """
    cursor = recipe_collection.find(
        {
            '$or': [
                {'$and': [
                    {'is_searchable': True},
                ]},
                {'$and': [
                    {'is_searchable': False},
                    {'user_id': user_id}
                ]},
            ],
            '$text': {'$search': keyword}
        },
        {'score': {'$meta': "textScore"}},
    ).sort([('likes', 1)])
    """
    cursor = recipe_collection.find(
        {
            '$and': [{
                '$or': [
                    {'$and': [
                        {'is_searchable': True},
                    ]},
                    {'$and': [
                        {'is_searchable': False},
                        {'user_id': user_id}
                    ]},
                ]
            }, {
                '$or': [
                    {'title': rgx},
                    {'ingredients': rgx},
                    {'description': rgx},
                    {'category_id': {'$in': good_tags}}
                ]
            }]
            # '$text': {'$search': keyword}
        },
        {'score': {'$meta': "textScore"}},
    ).sort([('likes', 1)])
    for recipe in cursor:
        recipes.append(recipe)

    return recipes


def find_recipe_by_id(recipe_id):
    """
    Принимает ID рецепта
    Возвращает информацию по рецепту
    """
    return recipe_collection.find_one({"_id": ObjectId(recipe_id)})


def get_category_by_id(category_id):
    """
    Получает id категории
    Возвращает всю информацию по ней
    """
    return tags_collection.find_one({'tag_id': int(category_id)})


def get_category_by_name(category_name):
    """
    Получает наименование категории
    Возвращает её id
    """
    tag = tags_collection.find_one({'name': str(category_name)})
    return tag['tag_id']


def get_categories():
    """
    Возвращает все категории (теги)
    """
    tags = []
    for tag in tags_collection.find({}).sort([('name', 1)]):
        tags.append(tag)
    return tags


def get_user_recipes(user_id, category_id=None):
    """
    Получает id пользователя и id категории
    Возвращает список всех рецептов пользователя, если задана категория - с фильтром по ней
    """
    recipes = []
    search_query = {'user_id': user_id}
    if category_id:
        search_query['category_id'] = category_id
    cursor = recipe_collection.find(search_query)
    for recipe in cursor:
        recipes.append(recipe)

    return recipes


def format_recipe_for_output(recipe):
    """
    Получает рецепт из базы
    Возвращает форматированную строку для вывода пользователю
    """
    recipe_txt = \
        'Наименование рецепта:\n' + recipe['title'] + '\n\n' \
        'Ингредиенты:\n' + recipe['ingredients'] + '\n\n' \
        'Описание:\n' + recipe['description'] + '\n\n' \
        'Кол-во лайков:\n' + str(recipe['likes']) + ' шт.\n\n'

    return recipe_txt


def like_recipe(user_id, recipe_id):
    """
    Получает ID пользователя, который ставит лайк и id рецепта, которому лайк предназначен
    Увеличивает у рецепта recipe_id кол-во лайков, если текущий пользователь еще не лайкал его
    TODO: внедрить проверку на то, что ранее не лайкал
    """
    recipe_collection.update_one({
        '_id': ObjectId(recipe_id)
    }, {
        '$inc': {
            'likes': 1
        }
    })
