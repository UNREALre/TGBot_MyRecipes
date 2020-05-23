#! /usr/bin/env python
# -*- coding: utf-8 -*-

from config import db
import datetime


class Recipe:

    id = ""
    user_id = ""
    user_name = ""
    title = ""
    ingredients = ""
    description = ""
    tag_id = 0  # читай: категория
    likes = 0
    is_searchable = False

    def save_recipe(self):
        """
        Сохраняет рецепт в базу
        Возвращает id сохраненного рецепта
        :return: id
        """
        recipe_collection = db['recipe']
        recipe_id = recipe_collection.insert_one({
            "user_id": self.user_id,
            "user_name": self.user_name,
            "title": self.title,
            "ingredients": self.ingredients,
            "description": self.description,
            "category_id": self.tag_id,
            "likes": 0,
            "is_searchable": self.is_searchable,
            "added": datetime.datetime.now(),
            "updated": datetime.datetime.now()
        }).inserted_id

        return recipe_id

