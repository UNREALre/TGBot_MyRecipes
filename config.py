#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import confuse
import urllib.parse
import pymongo
from logger import get_logger
from managers.VoiceRecognitionManager import build_models

project_root = os.path.dirname(os.path.abspath(__file__))
os.environ["MYRECIPEDIR"] = project_root
appConfig = confuse.Configuration('MyRecipe')

db_conn = dict()
db_conn['username'] = urllib.parse.quote_plus(str(appConfig['db']['user']))
db_conn['password'] = urllib.parse.quote_plus(str(appConfig['db']['pass']))
db_conn['host'] = str(appConfig['db']['host'])
db_conn['port'] = str(appConfig['db']['port'])
db_conn['name'] = str(appConfig['db']['name'])

client = pymongo.MongoClient(
    'mongodb://%s:%s@%s:%s/%s?authMechanism=SCRAM-SHA-1'
    %
    (db_conn['username'], db_conn['password'], db_conn['host'], db_conn['port'], db_conn['name'])
)

db = client[str(appConfig['db']['name'])]

rcp_logger = get_logger(__name__)

input_folder = 'data'
# Создаем HMM-модель для каждого слова из входной папки
# speech_models = build_models(input_folder)
speech_models = []
