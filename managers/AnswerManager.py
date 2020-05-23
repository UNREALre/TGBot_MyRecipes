#! /usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from config import rcp_logger, appConfig
from classes import Recipe
from classes import User
from managers.RecipeManager import (find_recipe, get_category_by_id,
                                    get_categories, get_category_by_name,
                                    find_recipe_by_id, format_recipe_for_output, like_recipe)
from managers.KeyboardManager import (return_keyboard, generate_categories_kb,
                                      generate_user_recipes_kb, generate_like_keyboard)

first_choice_keyboard = return_keyboard('first_choice_keyboard')
searchable_keyboard = return_keyboard('searchable_keyboard')
final_choice_keyboard = return_keyboard('final_choice_keyboard')
back_to_categories = return_keyboard('back_to_categories')
back_to_search_keyword = return_keyboard('back_to_search_keyword')

my_recipe = Recipe.Recipe()
rcp_user = User.User()

from_confirm = False  # флаг, означающий, что пользователь дошел (или не дошел) до стадии подтверждения

searchable_category = 0  # id категории, которую пользователь может выбрать на клавиатуре

selected_recipe = 0  # id рецепта, который пользователь может выбрать на клавиатуре

nothing_found_state_occur = False  # возврат к списку категорий из состояния ничего не найдено

rcp_keyword = ""  # возможный ключевик для поиска по рецептам


def response_generator(rcp_state, update):
    global nothing_found_state_occur

    if rcp_state == 'cancel':
        # Заканчиваем диалог
        update.message.reply_text('Возвращайтесь еще!', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    elif rcp_state == 'start':
        # Состояние начала диалога
        user_text = ''
        if rcp_user.id:
            user_text = '%s, добро пожаловать! У Вас %s добавленных рецептов. ' \
                        'У ваших рецептов %s лайков.\n\n' % (rcp_user.name, rcp_user.recipes_num, rcp_user.recipes_likes)
        update.message.reply_text(
            user_text +
            'Что Вы хотите сделать? Пожалуйста, сделайте свой выбор.\n'
            'Отправьте /cancel для прекращения диалога.\n\n',
            reply_markup=ReplyKeyboardMarkup(first_choice_keyboard, one_time_keyboard=True)
        )
        return str(appConfig['chat']['state']['FIRST_CHOICE'])

    elif rcp_state == 'new_recipe':
        # Состояние ожидания ввода названия рецепта
        update.message.reply_text('Как называется Ваш рецепт?', reply_markup=ReplyKeyboardRemove())
        return str(appConfig['chat']['state']['NEW_RECIPE'])

    elif rcp_state == 'recipe_components':
        # Состояние ожидания ввода ингредиентов рецепта
        update.message.reply_text('Из каких ингредиентов состоит рецепт?', reply_markup=ReplyKeyboardRemove())
        return str(appConfig['chat']['state']['NEW_RECIPE_COMPONENTS'])

    elif rcp_state == 'recipe_description':
        # Состояние ожидания ввода описания рецепта
        update.message.reply_text('Опишите как приготовить блюдо?', reply_markup=ReplyKeyboardRemove())
        return str(appConfig['chat']['state']['NEW_RECIPE_DESCRIPTION'])

    elif rcp_state == 'recipe_tag':
        # Состояние ожидания выбора пользователем категории рецепта
        tags_keyboard = generate_categories_kb()
        update.message.reply_text('К какой категории отнести рецепт?', reply_markup=ReplyKeyboardMarkup(tags_keyboard))
        return str(appConfig['chat']['state']['NEW_RECIPE_TAGS'])

    elif rcp_state == 'search_status':
        # Состояние ожидания выбора пользователем типа доступности рецепта
        if hasattr(update.message, 'reply_text'):
            update.message.reply_text('Разрешить другим пользователям находить в поиске ваш рецепт?\n\n', reply_markup=ReplyKeyboardMarkup(searchable_keyboard, one_time_keyboard=True))
        else:
            update.callback_query.edit_message_text('Разрешить другим пользователям находить в поиске ваш рецепт?\n\n', reply_markup=ReplyKeyboardMarkup(searchable_keyboard, one_time_keyboard=True))
        return str(appConfig['chat']['state']['NEW_RECIPE_IS_SEARCHABLE'])

    elif rcp_state == 'confirm_recipe':
        # Состояние ожидания подтверждения введенных данных, либо изменения чего-либо
        recipe_category = get_category_by_id(my_recipe.tag_id)
        update.message.reply_text('Посмотрите получившийся рецепт. Все верно?\n\n'
                                  'Наименование рецепта:\n' + my_recipe.title + '\n\n'
                                  'Ингредиенты:\n' + my_recipe.ingredients + '\n\n'
                                  'Описание:\n' + my_recipe.description + '\n\n'
                                  'Категория:\n' + recipe_category['name'] + '\n\n'
                                  'Рарзрешить поиск рецепта другим:\n' + ('Нет' if not my_recipe.is_searchable else 'Да'),
                                  reply_markup=ReplyKeyboardMarkup(final_choice_keyboard, one_time_keyboard=True))
        return str(appConfig['chat']['state']['NEW_RECIPE_CONFIRMATION'])

    elif rcp_state == 'recipe_created':
        # Рецепт успешно создан. Окончание диалога.
        update.message.reply_text('Рецепт успешно сохранен!\n\nДля создания нового или поиска рецепта напечатайте /start',
                                  reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    elif rcp_state == 'browse_my_recipes':
        # Поиск своего рецепта, состояние ожидания выбора пользователя списка категорий для поиска
        prefix_text = ""
        if nothing_found_state_occur:
            nothing_found_state_occur = False
            prefix_text = 'Извините, в выбранной категории не найдено ни одного рецепта!\n\n'

        tags_keyboard = generate_categories_kb()
        update.message.reply_text(prefix_text + 'Из какой категории рецепт?', reply_markup=ReplyKeyboardMarkup(tags_keyboard))
        return str(appConfig['chat']['state']['BROWSE_MY_RECIPES'])

    elif rcp_state == 'search_recipe':
        # Поиск рецепта по ключевым словам, состояние ожидания ввода ключевого слова
        prefix_text = ""
        if nothing_found_state_occur:
            nothing_found_state_occur = False
            prefix_text = 'Извините, по данному запросу не найдено ни одного рецепта!\n\n'

        update.message.reply_text(prefix_text + 'По какому запросу искать рецепт?', reply_markup=ReplyKeyboardRemove())
        return str(appConfig['chat']['state']['SEARCH_RECIPE'])

    elif rcp_state == 'my_search_by_cat':
        # Поиск своего рецепта при выбранной ранее категории
        recipes_kb = generate_user_recipes_kb(rcp_user.id, get_category_by_name(searchable_category))
        if recipes_kb:
            update.message.reply_text('Рецептуарий нашел список рецептов!', reply_markup=ReplyKeyboardMarkup(back_to_categories))
            update.message.reply_text('Ваши рецепты в данной категории', reply_markup=InlineKeyboardMarkup(recipes_kb))
            return str(appConfig['chat']['state']['CHOOSE_RECIPE'])
        else:
            nothing_found_state_occur = True
            return response_generator('browse_my_recipes', update)

    elif rcp_state == 'my_search_rcp_selected':
        # Поиск рецепта, состояние, когда пользователь выбрал уже рецепт, завершаем диалог
        # если текущий пользователь = автору, иначе предлагаем лайкнуть рецепт
        recipe = find_recipe_by_id(selected_recipe)
        recipe_formatted = format_recipe_for_output(recipe)

        query = update.callback_query
        if query.from_user.id == recipe['user_id']:
            query.edit_message_text(recipe_formatted + 'Для возобновления работы Рецептуария введите /start')
            return ConversationHandler.END
        else:
            like_kb = generate_like_keyboard(query.from_user.id, selected_recipe)
            query.edit_message_text(recipe_formatted + 'Понравился рецепт? Поставьте ему лайк!', reply_markup=InlineKeyboardMarkup(like_kb))
            return str(appConfig['chat']['state']['LIKE_RECIPE'])

    elif rcp_state == 'search_by_keyword':
        # Поиск по базе Рецептуария по ключевому слову
        recipes_kb = generate_user_recipes_kb(rcp_user.id, None, rcp_keyword)
        if recipes_kb:
            update.message.reply_text('Рецептуарий нашел список рецептов!', reply_markup=ReplyKeyboardMarkup(back_to_search_keyword))
            update.message.reply_text('Выберите нужный рецепт', reply_markup=InlineKeyboardMarkup(recipes_kb))
            return str(appConfig['chat']['state']['CHOOSE_SEARCH_RESULTS'])
        else:
            nothing_found_state_occur = True
            return response_generator('search_recipe', update)

    elif rcp_state == 'store_user_like':
        return ConversationHandler.END


def rcp_help(update, context):
    update.message.reply_text(
        'Приветствую Вас! Я - рецептуарий! Здесь Вы сможете хранить свои рецепты.',
        reply_markup=ReplyKeyboardRemove()
    )


def start(update, context):
    rcp_user.prefill_user(update.message.from_user)
    if rcp_user.recipes_num and not first_choice_keyboard.count(['Посмотреть мои рецепты']):
        first_choice_keyboard.append(['Посмотреть мои рецепты'])

    return response_generator('start', update)


def choice_one(update, context):
    user = update.message.from_user
    rcp_logger.info('Пользователь %s выбрал %s' % (user.username, update.message.text))
    if update.message.text == 'Добавить рецепт':
        return response_generator('new_recipe', update)
    elif update.message.text == 'Посмотреть мои рецепты':
        return response_generator('browse_my_recipes', update)
    else:
        return response_generator('search_recipe', update)


def new_recipe_name(update, context):
    user = update.message.from_user

    my_recipe.user_id = user.id
    my_recipe.user_name = user.username
    my_recipe.title = update.message.text

    rcp_logger.info('Пользователь %s ввёл имя рецепта %s' % (user.username, update.message.text))

    return response_generator('confirm_recipe', update) if from_confirm else response_generator('recipe_components', update)


def new_components(update, context):
    user = update.message.from_user
    my_recipe.ingredients = update.message.text

    rcp_logger.info('Пользователь %s ввёл список ингредиентов \"%s\"' % (user.username, update.message.text))

    return response_generator('confirm_recipe', update) if from_confirm else response_generator('recipe_description',
                                                                                                update)


def new_descriptions(update, context):
    user = update.message.from_user
    my_recipe.description = update.message.text

    rcp_logger.info('Пользователь %s ввёл сам рецепт \"%s\"' % (user.username, update.message.text))

    return response_generator('confirm_recipe', update) if from_confirm else response_generator('recipe_tag',
                                                                                                update)


def new_tags(update, context):
    user = update.message.from_user
    my_recipe.tag_id = get_category_by_name(update.message.text)

    rcp_logger.info('Пользователь %s выбрал категорию \"%s\"' % (user.username, update.message.text))

    return response_generator('confirm_recipe', update) if from_confirm else response_generator('search_status',
                                                                                                update)


def searchable_status(update, context):
    user = update.message.from_user
    my_recipe.is_searchable = False if update.message.text == 'Нет, рецепт приватный' else True

    rcp_logger.info('Пользователь %s ответил на вопрос о приватности рецепта: %s' % (user.username, update.message.text))

    return response_generator('confirm_recipe', update)


def confirm_choice(update, context):
    global from_confirm
    from_confirm = True

    user = update.message.from_user
    rcp_logger.info('Пользователь %s выбрал %s' % (user.username, update.message.text))

    if update.message.text == 'Да, сохранить рецепт':
        my_recipe.save_recipe()
        return response_generator('recipe_created', update)
    elif update.message.text == 'Нет, изменить название':
        return response_generator('new_recipe', update)
    elif update.message.text == 'Нет, изменить ингредиенты':
        return response_generator('recipe_components', update)
    elif update.message.text == 'Нет, изменить описание':
        return response_generator('recipe_description', update)
    elif update.message.text == 'Нет, изменить категорию':
        return response_generator('recipe_tag', update)
    elif update.message.text == 'Нет, изменить приватность':
        return response_generator('search_status', update)


def search_recipe(update, context):
    global rcp_keyword
    rcp_keyword = update.message.text

    user = update.message.from_user
    rcp_logger.info('Пользователь %s пытается найти рецепт по запросу %s' % (user.username, update.message.text))

    return response_generator('search_by_keyword', update)


def browse_my_rcp_category(update, context):
    global searchable_category
    searchable_category = update.message.text
    user = update.message.from_user
    rcp_logger.info('Пользователь %s выбирает категорию своих рецептов %s' % (user.username, update.message.text))

    return response_generator('my_search_by_cat', update)


def choose_recipe(update, context):
    global selected_recipe
    user = update.callback_query.from_user
    query = update.callback_query
    query.answer()

    selected_recipe = format(query.data)

    rcp_logger.info('Пользователь %s выбирает рецепт с ID = %s' % (user.username, selected_recipe))

    context.bot.send_message(chat_id=update.effective_chat.id, text="Спасибо, что воспользовались Рецептуарием!", reply_markup=ReplyKeyboardRemove())

    return response_generator('my_search_rcp_selected', update)


def return_to_categories(update, context):
    return response_generator('browse_my_recipes', update)


def choose_search_result(update, context):
    global selected_recipe
    user = update.callback_query.from_user
    query = update.callback_query
    query.answer()

    selected_recipe = format(query.data)

    rcp_logger.info('Пользователь %s выбирает из поиска рецепт с ID = %s' % (user.username, selected_recipe))

    context.bot.send_message(chat_id=update.effective_chat.id, text="Спасибо, что воспользовались Рецептуарием!", reply_markup=ReplyKeyboardRemove())

    return response_generator('my_search_rcp_selected', update)


def return_to_search(update, context):
    return response_generator('search_recipe', update)


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
    return response_generator('store_user_like', update)


def cancel(update, context):
    user = update.message.from_user
    rcp_logger.info('Пользователь %s завершил диалог' % user.first_name)

    return response_generator('cancel', update)
