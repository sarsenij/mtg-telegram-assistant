import tables, strings, util, telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatAction
from peewee import *
from emoji import emojize
from telegram.ext import CallbackContext
from config import config
import cacheable


def start_pvt(update: Update, context: CallbackContext):
    user = util.is_user_known(update,context)
    if user:
        text = strings.Start.start_pvt
        context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)


@util.send_action(ChatAction.TYPING)
def name(update: Update, context: CallbackContext):
    user = util.is_user_known(update,context)
    if user:
        args = update.message.text.split(" ", 1)
        if len(args) == 1:
            context.bot.send_message(chat_id=update.message.chat_id,
                             text=strings.Name.name_invalid,
                             parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            name = args[1]
            user = tables.User.get(tables.User.user_id == update.message.from_user.id)
            user.name = name
            user.save()
            context.bot.send_message(chat_id=update.message.chat_id,
                             text=strings.Name.name_set.format(name),
                             parse_mode=telegram.ParseMode.MARKDOWN)


@util.send_action(ChatAction.TYPING)
def arena(update: Update, context: CallbackContext):
    args = update.message.text.split(" ", 1)
    user = util.is_user_known(update,context)
    if user:
        user = tables.User.get(tables.User.user_id == update.message.from_user.id)
        if len(args) == 1 and not user.arena:
            context.bot.send_message(chat_id=update.message.chat_id,
                             text=strings.Arena.arena_invalid,
                             parse_mode=telegram.ParseMode.MARKDOWN)
        elif len(args) == 1:
            context.bot.send_message(chat_id=update.message.chat_id,
                            text=strings.Inline.player_card_text.format(user.name if not None else "",
                                                                        user.arena if not None else ""),
                            parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            arena = args[1]
            user.arena = arena
            user.save()
            context.bot.send_message(chat_id=update.message.chat_id,
                             text=strings.Arena.arena_set.format(arena),
                             parse_mode=telegram.ParseMode.MARKDOWN)


@util.send_action(ChatAction.TYPING)
def help_pvt(update: Update, context: CallbackContext):
    #if update.message.from_user.id in cacheable.get_admin_ids(context.bot):
    #    button_list = [InlineKeyboardButton("user", callback_data="help_user"),
    #                   InlineKeyboardButton("admin", callback_data="help_admin")]
    #    reply_markup = InlineKeyboardMarkup(util.build_menu(button_list, n_cols=2))
    #    text = strings.Help.admin_help
    #    context.bot.send_message(chat_id=update.message.chat_id,
    #                     text=emojize(text, use_aliases=True),
    #                     parse_mode=telegram.ParseMode.MARKDOWN,
    #                     reply_markup=reply_markup)
    #else:
    text = strings.Help.user_help
    context.bot.send_message(chat_id=update.message.chat_id,
                     text=emojize(text, use_aliases=True),
                     parse_mode=telegram.ParseMode.MARKDOWN)

def add(update: Update, context: CallbackContext):
    if update.message.from_user.id in config["master"]:
        args = update.message.text.split(" ")
        if len(args) >= 3:
            first_name = " ".join(args[2:])
            user_id = args[1]
            try:
                tables.User.get(tables.User.user_id == user_id)
            except DoesNotExist:
                tables.User.create(user_id=user_id,
                        group=0,
                        name=first_name)
            context.bot.send_message(chat_id=update.message.chat_id, text=strings.Admin.user_added.format(first_name), parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text=strings.Admin.missing_arguments, parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=strings.Admin.not_allowed, parse_mode=telegram.ParseMode.MARKDOWN)


            


def help_cb(update: Update, context: CallbackContext):
    query = update.callback_query
    button_list = [InlineKeyboardButton("user", callback_data="help_user"),
                   InlineKeyboardButton("admin", callback_data="help_admin")]
    reply_markup = InlineKeyboardMarkup(util.build_menu(button_list, n_cols=2))
    if "help_user" in query.data:
        reply = strings.Help.user_help
        pass
    else:
        reply = strings.Help.admin_help
        pass
    try:
        context.bot.edit_message_text(text=reply, chat_id=query.message.chat_id,
                              message_id=query.message.message_id, reply_markup=reply_markup,
                              parse_mode=telegram.ParseMode.MARKDOWN)
    except telegram.error.BadRequest:
        context.bot.answer_callback_query(callback_query_id=update.callback_query.id)
