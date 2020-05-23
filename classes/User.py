#! /usr/bin/env python
# -*- coding: utf-8 -*-

from config import db
from managers.UserManager import count_user_recipes, count_user_recipes_likes


class User:

    id = ""
    name = ""
    recipes_num = 0
    recipes_likes = 0

    def prefill_user(self, tg_user):
        """
        Получает данные о пользователе из чата, заполняет ими нужные свойства пользователя
        """
        self.id = tg_user.id
        self.name = tg_user.username
        self.recipes_num = count_user_recipes(self.id)
        self.recipes_likes = count_user_recipes_likes(self.id)

