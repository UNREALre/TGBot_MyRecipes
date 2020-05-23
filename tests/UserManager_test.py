#! /usr/bin/env python
# -*- coding: utf-8 -*-

from managers.UserManager import count_user_recipes, count_user_recipes_likes


def test_count_user_recipes():
    print(count_user_recipes(99760649))


def test_count_user_recipes_likes():
    print(count_user_recipes_likes(99760649))


test_count_user_recipes()
test_count_user_recipes_likes()