from functools import wraps
from config import config
from peewee import *
import tables
import strings
import telegram

def send_action(action):
    """Sends `action` while processing func command."""
    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)
        return command_func
    return decorator


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in config["master"]:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped

def is_user_known(update,context,ask_if_new=False):
    new = False
    try:
        user = tables.User.get(tables.User.user_id == update.message.from_user.id)
        if user.group == 0 and update.message.chat.type != 'private':
            user.group = update.message.chat_id
            user.save()
    except DoesNotExist:
        if update.message.chat.type != 'private':
            tables.User.create(user_id=update.message.from_user.id,
                               group=update.message.chat_id,
                               name=update.message.from_user.first_name)
            new = True
            user = tables.User.get(tables.User.user_id == update.message.from_user.id)

        else:
            text = strings.Global.user_not_exist
            text += strings.Start.start_id.format(update.message.from_user.id,update.message.from_user.first_name)
            context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
            if ask_if_new:
                return new, False
            else:
                return False
    if ask_if_new:
        return new, user
    else:
        return user
