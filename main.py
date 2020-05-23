#! /usr/bin/env python
# -*- coding: utf-8 -*-

from config import appConfig, rcp_logger
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
import managers.AnswerManager as am
from managers.KeyboardManager import return_keyboard

first_choice_keyboard = return_keyboard('first_choice_keyboard', True)
final_choice_keyboard = return_keyboard('final_choice_keyboard', True)
back_to_categories = return_keyboard('back_to_categories', True)
back_to_search_keyword = return_keyboard('back_to_search_keyword', True)


def error(update, context):
    """
    Логирование ошибок
    """
    rcp_logger.warning('Ошибка: %s ! Данные %s' % (context.error, update))


def main():
    updater = Updater(str(appConfig['tg']['key']), use_context=True)
    dispatcher = updater.dispatcher  # Get the dispatcher to register handlers

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', am.start)],

        states={
            str(appConfig['chat']['state']['FIRST_CHOICE']): [CommandHandler('cancel', am.cancel), MessageHandler(Filters.regex('^(' + first_choice_keyboard + '|Посмотреть мои рецепты)$'), am.choice_one)],
            str(appConfig['chat']['state']['NEW_RECIPE']): [CommandHandler('cancel', am.cancel), MessageHandler(Filters.text, am.new_recipe_name)],
            str(appConfig['chat']['state']['NEW_RECIPE_COMPONENTS']): [CommandHandler('cancel', am.cancel), MessageHandler(Filters.text, am.new_components)],
            str(appConfig['chat']['state']['NEW_RECIPE_DESCRIPTION']): [CommandHandler('cancel', am.cancel), MessageHandler(Filters.text, am.new_descriptions)],
            str(appConfig['chat']['state']['NEW_RECIPE_TAGS']): [CommandHandler('cancel', am.cancel), MessageHandler(Filters.text, am.new_tags)],
            str(appConfig['chat']['state']['NEW_RECIPE_IS_SEARCHABLE']): [CommandHandler('cancel', am.cancel), MessageHandler(Filters.text, am.searchable_status)],
            str(appConfig['chat']['state']['NEW_RECIPE_CONFIRMATION']): [CommandHandler('cancel', am.cancel), MessageHandler(Filters.regex('^(' + final_choice_keyboard + ')$'), am.confirm_choice)],
            str(appConfig['chat']['state']['SEARCH_RECIPE']): [CommandHandler('cancel', am.cancel), MessageHandler(Filters.text, am.search_recipe)],
            str(appConfig['chat']['state']['BROWSE_MY_RECIPES']): [CommandHandler('cancel', am.cancel), MessageHandler(Filters.text, am.browse_my_rcp_category)],
            str(appConfig['chat']['state']['CHOOSE_RECIPE']): [CommandHandler('cancel', am.cancel),
                                                               CallbackQueryHandler(am.choose_recipe),
                                                               MessageHandler(Filters.text, am.return_to_categories)],
            str(appConfig['chat']['state']['CHOOSE_SEARCH_RESULTS']): [CommandHandler('cancel', am.cancel),
                                                                       CallbackQueryHandler(am.choose_search_result),
                                                                       MessageHandler(Filters.text, am.return_to_search)],
            str(appConfig['chat']['state']['LIKE_RECIPE']): [CommandHandler('cancel', am.cancel),
                                                             CallbackQueryHandler(am.store_user_like)],
        },

        fallbacks=[CommandHandler('cancel', am.cancel)],

        conversation_timeout=300
    )

    dispatcher.add_handler(conv_handler)

    dispatcher.add_handler(CommandHandler('help', am.rcp_help))

    dispatcher.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
