#! /usr/bin/env python
# -*- coding: utf-8 -*-

from config import db
import json
import os
import pymongo

project_root = os.path.dirname(os.path.abspath('config.yaml'))
recipe_collection = db['recipe']
tags_collection = db['tags']


def create_indexes():
    recipe_collection.create_index([('title', 'text'), ('ingredients', 'text'), ('description', 'text')])
    tags_collection.create_index([('name', 'text')])
    tags_collection.create_index([('tag_id', pymongo.ASCENDING)], unique=True)


def fill_tags():
    file = open('resources/tags.json', encoding='utf-8')
    tags = json.load(file)
    for tag in tags:
        exist = tags_collection.find_one({'tag_id': tag['tag_id']})
        if exist:
            tags_collection.update_one({
                '_id': exist['_id']
            }, {
                '$set': tag
            })
        else:
            tags_collection.insert_one(tag)


def prepare_for_likes():
    """
    Заносим 1 запись и создаем индекс для хранения кто кому ставил лайки
    """
    pass


fill_tags()
create_indexes()

