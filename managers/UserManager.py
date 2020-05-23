#! /usr/bin/env python
# -*- coding: utf-8 -*-

from config import db

recipe_collection = db['recipe']


def count_user_recipes(user_id):
    """
    Принимает id от пользователя из TG, пытается найти его рецепты
    Возвращает количество рецептов
    """
    cursor = recipe_collection.aggregate([
        {
            '$match': {'user_id': user_id}
        },
        {
            '$group': {
                '_id': 'user_id',
                'count': {'$sum': 1}
            }
        }
    ])
    counter = 0
    for recipe in cursor:
        counter += recipe['count']

    return counter


def count_user_recipes_likes(user_id):
    """
    Получает id пользователя
    Возвращает количество лайков к рецептам пользователя
    """
    likes = 0
    cursor = recipe_collection.aggregate([
        {'$match': {'user_id': user_id}},
        {'$group': {
            '_id': '$user_id',
            'likes': {'$sum': '$likes'}
        }}
    ])
    for recipe in cursor:
        likes += recipe['likes']

    return likes

