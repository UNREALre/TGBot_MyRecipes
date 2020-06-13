#! /usr/bin/env python
# -*- coding: utf-8 -*-

import managers.ResponseGenerator as RG
import os
from classes.VoiceFile import VoiceFile
from telegram import ReplyKeyboardRemove, InlineKeyboardMarkup, ParseMode
from config import rcp_logger, appConfig, speech_models
from managers.RecipeManager import (get_category_by_name, like_recipe)
from managers.VoiceRecognitionManager import fire_recognition

from_confirm = False


def rcp_help(update, context):
    update.message.reply_text(
        'Приветствую Вас! Я - Рецептуарий! Здесь Вы сможете хранить свои рецепты.\n'
        'Сейчас я расскажу Вам основы работы со мной. Все довольно просто!\n'
        'Любое начала работы со мной осуществляется вводом команды /start \n'
        'Хотите ли Вы добавить новый рецепт или найти что-то, начинается все со /start \n'
        'Написав /start Вы запустите диалог со мной. Я буду предлагать Вам выбирать разные варианты '
        'продолжения разговора (создать рецепт, найти рецепт и т.п.)\n'
        'Если Вы поймете, что хотите прекратить диалог или начать все сначала, просто напечатайте /cancel\n'
        'Находясь в любом уровне диалога, просто напишите /cancel и Вы вернетесь к началу.\n\n'
        'Я позволяю сохранять в базе ваши рецепты, чтобы в последующем иметь к ним быстрый доступ.\n'
        'При создании Вы можете пометить рецепт открытым для поиска, тогда другие пользователи '
        'Рецептуария смогут по ключевым словам найти ваш рецепт, прочитать его и поставить Лайки!\n\n'
        'Вы можете вводить в ключевые слова для поиска как ингредиенты, так и названия целых категорий, '
        'которые представлены в рецептуарии, например: "суп", "выпечка", "паста". Если я найду совпадения '
        'по названию категории, то включу в результаты поиска все рецепты из запрашиваемой категории.\n\n'
        'По вашим ранее добавленным рецептам существует удобная навигация по категориям, просто '
        'выберите нужную категорию, а затем выберите рецепт, который Вас интересует.\n\n'
        'Если у Вас будут какие-то пожелания и замечания - пишите моему создателю @UNREALre',
        reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML
    )


def start(update, context):
    RG.rcp_user.prefill_user(update.message.from_user)
    if RG.rcp_user.recipes_num and not RG.first_choice_keyboard.count(['Посмотреть мои рецепты']):
        RG.first_choice_keyboard.append(['Посмотреть мои рецепты'])

    return RG.response_generator('start', update)


def choice_one(update, context):
    user = update.message.from_user
    rcp_logger.info('Пользователь %s выбрал %s' % (user.username, update.message.text))
    if update.message.text == 'Добавить рецепт':
        return RG.response_generator('new_recipe', update)
    elif update.message.text == 'Посмотреть мои рецепты':
        return RG.response_generator('browse_my_recipes', update)
    else:
        return RG.response_generator('search_recipe', update)


def new_recipe_name(update, context):
    user = update.message.from_user

    RG.my_recipe.user_id = user.id
    RG.my_recipe.user_name = user.username
    RG.my_recipe.title = update.message.text

    rcp_logger.info('Пользователь %s ввёл имя рецепта %s' % (user.username, update.message.text))

    return RG.response_generator('confirm_recipe', update) if from_confirm else RG.response_generator('recipe_components', update)


def new_components(update, context):
    user = update.message.from_user
    RG.my_recipe.ingredients = update.message.text

    rcp_logger.info('Пользователь %s ввёл список ингредиентов \"%s\"' % (user.username, update.message.text))

    return RG.response_generator('confirm_recipe', update) if from_confirm else RG.response_generator('recipe_description',
                                                                                                update)


def new_descriptions(update, context):
    user = update.message.from_user
    RG.my_recipe.description = update.message.text

    rcp_logger.info('Пользователь %s ввёл сам рецепт \"%s\"' % (user.username, update.message.text))

    return RG.response_generator('confirm_recipe', update) if from_confirm else RG.response_generator('recipe_tag',
                                                                                                update)


def new_tags(update, context):
    user = update.message.from_user
    RG.my_recipe.tag_id = get_category_by_name(update.message.text)

    rcp_logger.info('Пользователь %s выбрал категорию \"%s\"' % (user.username, update.message.text))

    return RG.response_generator('confirm_recipe', update) if from_confirm else RG.response_generator('search_status',
                                                                                                update)


def searchable_status(update, context):
    user = update.message.from_user
    RG.my_recipe.is_searchable = False if update.message.text == 'Нет, рецепт приватный' else True

    rcp_logger.info('Пользователь %s ответил на вопрос о приватности рецепта: %s' % (user.username, update.message.text))

    return RG.response_generator('confirm_recipe', update)


def confirm_choice(update, context):
    global from_confirm
    from_confirm = True

    user = update.message.from_user
    rcp_logger.info('Пользователь %s выбрал %s' % (user.username, update.message.text))

    if update.message.text == 'Да, сохранить рецепт':
        RG.my_recipe.save_recipe()
        return RG.response_generator('recipe_created', update)
    elif update.message.text == 'Нет, изменить название':
        return RG.response_generator('new_recipe', update)
    elif update.message.text == 'Нет, изменить ингредиенты':
        return RG.response_generator('recipe_components', update)
    elif update.message.text == 'Нет, изменить описание':
        return RG.response_generator('recipe_description', update)
    elif update.message.text == 'Нет, изменить категорию':
        return RG.response_generator('recipe_tag', update)
    elif update.message.text == 'Нет, изменить приватность':
        return RG.response_generator('search_status', update)


def search_recipe(update, context):
    global rcp_keyword
    rcp_keyword = update.message.text

    user = update.message.from_user
    rcp_logger.info('Пользователь %s пытается найти рецепт по запросу %s' % (user.username, update.message.text))

    return RG.response_generator('search_by_keyword', update)


def browse_my_rcp_category(update, context):
    global searchable_category
    searchable_category = update.message.text
    user = update.message.from_user
    rcp_logger.info('Пользователь %s выбирает категорию своих рецептов %s' % (user.username, update.message.text))

    return RG.response_generator('my_search_by_cat', update)


def choose_recipe(update, context):
    global selected_recipe
    user = update.callback_query.from_user
    query = update.callback_query
    query.answer()

    selected_recipe = format(query.data)

    rcp_logger.info('Пользователь %s выбирает рецепт с ID = %s' % (user.username, selected_recipe))

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Спасибо, что воспользовались Рецептуарием!",
                             reply_markup=ReplyKeyboardRemove())

    return RG.response_generator('my_search_rcp_selected', update)


def return_to_categories(update, context):
    return RG.response_generator('browse_my_recipes', update)


def choose_search_result(update, context):
    global selected_recipe
    user = update.callback_query.from_user
    query = update.callback_query
    query.answer()

    selected_recipe = format(query.data)

    rcp_logger.info('Пользователь %s выбирает из поиска рецепт с ID = %s' % (user.username, selected_recipe))

    context.bot.send_message(chat_id=update.effective_chat.id, text="Спасибо, что воспользовались Рецептуарием!", reply_markup=ReplyKeyboardRemove())

    return RG.response_generator('my_search_rcp_selected', update)


def return_to_search(update, context):
    return RG.response_generator('search_recipe', update)


def store_user_like(update, context):
    global selected_recipe
    user = update.callback_query.from_user
    query = update.callback_query
    query.answer()

    user_id, recipe_id = format(query.data).split('~')
    like_recipe(user_id, recipe_id)

    rcp_logger.info('Пользователь %s лайкает рецепт с ID = %s' % (user.username, recipe_id))

    context.bot.send_message(chat_id=update.effective_chat.id, text="Спасибо за лайк!", reply_markup=ReplyKeyboardRemove())
    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([]))
    return RG.response_generator('store_user_like', update)


def cancel(update, context):
    user = update.message.from_user
    rcp_logger.info('Пользователь %s завершил диалог' % user.first_name)

    return RG.response_generator('cancel', update)


def rcp_recognition(update, context):
    """Тестирование распознавания речи"""
    user = update.message.from_user
    rcp_logger.info('Пользователь {} отправил голосовое сообщение'.format(user.first_name))
    print(update)
    voice_file = VoiceFile(update.message.voice.file_id,
                           update.message.voice.file_unique_id,
                           update.message.voice.duration,
                           update.message.voice.mime_type,
                           update.message.voice.file_size,
                           str(appConfig['tg']['key']),
                           str(appConfig['app']['paths']['voice']))
    wav_file = voice_file.get_file()
    if os.path.isfile(wav_file):
        prediction = fire_recognition(wav_file, speech_models)
        out_msg = "Мне кажется или Вы сказали \"{}\" ?".format(prediction)
        # os.remove(wav_file)
    else:
        out_msg = "Извините, что-то пошло не так..."

    update.message.reply_text(
        out_msg + '\n\n'
        'На данный момент я могу распознать только слова: apple, banana, kiwi, lime, orange, peach, pineapple\n'
        'Убедитесь, что длина отправленного аудио-сообщения больше 2 секунд!',
        reply_markup=ReplyKeyboardRemove()
    )