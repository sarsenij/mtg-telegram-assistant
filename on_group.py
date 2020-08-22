import telegram, tables, strings, util, requests, logging, emoji, cacheable
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram import ChatAction
from peewee import *
from emoji import emojize
from bs4 import BeautifulSoup
from telegram.ext import CallbackContext
from config import config
from mwt import MWT

logger = logging.getLogger(__name__)


def welcome_message(update: Update, context: CallbackContext):
    if strings.Global.welcome_message:
        text = emoji.emojize(strings.Global.welcome_message.format(update.message.from_user.first_name),
                             use_aliases=True)
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=text,
                                 parse_mode=telegram.ParseMode.MARKDOWN)


def start_group(update: Update, context: CallbackContext):
    new, user = util.is_user_known(update,context,ask_if_new=True)
    if not new and user:
        context.bot.send_message(chat_id=update.message.chat_id,
                text=strings.Global.user_already_exist,
                parse_mode=telegram.ParseMode.MARKDOWN)
    elif new:
        context.bot.send_message(chat_id=update.message.chat_id,
                text=strings.Global.welcome_message.format(user.name),
                parse_mode=telegram.ParseMode.MARKDOWN)

@MWT(timeout=60*15)
def social(update: Update, context: CallbackContext):
    user = util.is_user_known(update,context)
    if user:
        if config["social"]:
            text = strings.Help.social_links
            social_message = "\n".join("[{}]({})".format(key,config["social"][key]) for key in sorted(config["social"].keys()))

            text += social_message
        else:
            text = strings.Help.no_social_links
        print(text)
        context.bot.send_message(chat_id=update.message.chat_id, text=emojize(text, use_aliases=True),
                                 parse_mode=telegram.ParseMode.MARKDOWN,
                                 disable_web_page_preview=True)


@util.send_action(ChatAction.TYPING)
def friend_list(update: Update, context: CallbackContext):
    user = util.is_user_known(update,context)
    text = cacheable.build_friendlist(update, context)
    context.bot.send_message(chat_id=update.message.chat_id, text=emojize(text, use_aliases=True),
                             parse_mode=telegram.ParseMode.HTML,
                             disable_web_page_preview=True)


@util.send_action(ChatAction.TYPING)
def arena_status(update: Update, context: CallbackContext):
    user = is_user_known(update,context)
    page = requests.get(config.statuspage, headers=config.headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    message = ":computer: "+strings.Arena.arena_status+" :computer:\n\n"
    # search all services under maintenance
    for foo in soup.find_all('div', attrs={'class': 'component-inner-container status-blue'}):
        bar = foo.find('span', attrs={'class': ['name', 'component-status ']})
        message += ":x: {} - {}\n".format(bar.text.strip(), strings.Arena.server_maintenance)

    # search all operational services
    for foo in soup.find_all('div', attrs={'class': 'component-inner-container status-green'}):
        bar = foo.find('span', attrs={'class': ['name', 'component-status ']})
        message += ":white_check_mark: {} - {}\n".format(bar.text.strip(), strings.Arena.server_ok)

    keyboard = [[InlineKeyboardButton(strings.Arena.goto_statuspage, url=config.statuspage)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=update.message.chat_id, text=emojize(message, use_aliases=True),
                             parse_mode=telegram.ParseMode.MARKDOWN,
                             reply_markup=reply_markup,
                             disable_web_page_preview=True)
def register_users(update: Update, context: CallbackContext):
    user = util.is_user_known(update,context)
