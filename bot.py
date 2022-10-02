import logging
import os

import telegram
import json
import re
import requests
import pyshorteners
import validators

from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from validators import ValidationFailure

from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = 'XXXX'

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    name = update.effective_user['first_name']
    user_id = update.effective_user['id']
    url_short = short_url('https://www.amazon.es/?&_encoding=UTF8&tag=guille21497-21&linkCode=ur2&linkId=8e9bc8f12992fadb5454eb4c85dc0d0c&camp=3638&creative=24630')
    msg = f"*Introduce una URL de un producto de Amazon y te la devolveré con mi referido* 💰 \n\n URL genérica de Amazon: \n🔗 {url_short}"
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="Markdown",
                            disable_web_page_preview=True,
                            text=msg)
    msg2 = f"*Recuerda:* \n 📲 Esta URL solo funciona si compras en el dispositivo donde la abres.\n 🕗 Dura 24h desde que entras al enlace. Si pasan las 24h vuelve a pinchar al enlace antes de comprar. \n 📩 Puedes copiarla y enviarla al dispositivo (PC o móvil) desde el que se realizará la commpra."
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="Markdown",
                            text=msg2)

def help(update, context):
    name = update.effective_user['first_name']
    user_id = update.effective_user['id']
    msg = f"*Introduce una URL de un producto de Amazon y te la devolveré con mi referido* 💰 \n - Si el enlace no es correcto o introduces cualquier otro mensaje te daré una URL genérica de Amazon con la que si compras cualquier cosa en menos de 24h desde el dispositivo que entra al enlace sirve igual. \n - Puedes copiar y enviar los enlaces generados aquí al dispositivo donde se vayan a realizar las compras."
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="Markdown",
                            text=msg)

def test(update, context):
    name = update.effective_user['first_name']
    user_id = update.effective_user['id']
    uri = "amzn.eu/d/c1y73vs"
    ht = "https://"
    tal = is_string_an_url(uri)
    context.bot.sendMessage(chat_id=user_id,
                                parse_mode="Markdown",
                                text=tal)

    if is_string_an_url(uri):
        r = requests.get(uri)
        context.bot.sendMessage(chat_id=user_id,
                            parse_mode="Markdown",
                            text=r.url)
    elif is_string_an_url(ht+uri):
        r = requests.get(ht+uri)
        context.bot.sendMessage(chat_id=user_id,
                            parse_mode="Markdown",
                            text=r.url)
    else:
        msg = f"*TEST*"
        context.bot.sendMessage(chat_id=user_id,
                                parse_mode="Markdown",
                                text=msg)

def is_string_an_url(url_string: str) -> bool:
    result = validators.url(url_string)

    if isinstance(result, ValidationFailure):
        return False

    return result


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def check_message(update, context):
    ht = "https://"
    name = update.effective_user['first_name']
    user_id = update.effective_user['id']

    text = update.message.text
    logger.info(f"{name} sent a msg: {text}")

    text_s = text.strip()
    domain = "{0.netloc}".format(urlsplit(text_s))
    if domain.find("amazon.") != -1:
        amazon_referral(update, context, text_s, domain)
    else:
        if is_string_an_url(text):
            r = requests.get(text)
            text_2 = r.url
            text_2s = text_2.strip()
            domain_2 = "{0.netloc}".format(urlsplit(text_2s))
            if domain_2.find("amazon.") != -1:
                amazon_referral(update, context, text_2s, domain_2)
            else:
                url_incorrecta(update, context)
        elif is_string_an_url(ht+text):
            r = requests.get(ht+text)
            text_3 = r.url
            text_3s = text_3.strip()
            domain_3 = "{0.netloc}".format(urlsplit(text_3s))
            if domain_3.find("amazon.") != -1:
                amazon_referral(update, context, text_3s, domain_3)
            else:
                url_incorrecta(update, context)
        else:
            url_incorrecta(update, context)


def url_incorrecta(update, context):
    name = update.effective_user['first_name']
    user_id = update.effective_user['id']

    msg = f"La URL introducida no es correcta. \n "
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="Markdown",
                            text=msg)
    url_short = short_url("https://www.amazon.es/?&_encoding=UTF8&tag=guille21497-21&linkCode=ur2&linkId=8e9bc8f12992fadb5454eb4c85dc0d0c&camp=3638&creative=24630")
    msg = f"URL genérica de Amazon: \n\n🔗 {url_short}"
    context.bot.sendMessage(chat_id=user_id,
                                parse_mode="Markdown",
                                text=msg)
    msg2 = f"*Recuerda:* \n 📲 Esta URL solo funciona si compras en el dispositivo donde la abres.\n 🕗 Dura 24h desde que entras al enlace. Si pasan las 24h vuelve a pinchar al enlace antes de comprar. \n 📩 Puedes copiarla y enviarla al dispositivo (PC o móvil) desde el que se realizará la commpra."
    context.bot.sendMessage(chat_id=user_id,
                                parse_mode="Markdown",
                                text=msg2)

def location(update, context):
    name = update.effective_user['first_name']
    username = update.effective_user['username']
    logger.info(f"{name} sent location")
    user_id = update.effective_user['id']
    user_lat = update.message.location.latitude
    user_lon = update.message.location.longitude
    update_user_location(user_id, username, user_lat, user_lon)
    msg = "Perfecto, intentaré acordarme de que estás ahí."
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="HTML",
                            text=msg)

# AMAZON

def scrap_amazon(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/74.0.3729.169 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5", }
    url = "https://" + url
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    try:
        title = soup.find(id="productTitle").get_text()
        price_whole = soup.find('span', {'class': 'a-price-whole'}).text.strip()
        price_praction = soup.find('span', {'class': 'a-price-fraction'}).text.strip()
        image = list(json.loads(soup.find(id="imgTagWrapperId").img.get('data-a-dynamic-image')).keys())[0]
    except AttributeError:
        title = 'NA'
        price_whole = 'NA'
        price_praction = 'NA'
        image = 'NA'
    price = price_whole + price_praction
    return title, image, price


def clear_url(url, domain):
    regex = re.compile("(/[dg]p/[^/?]+)")
    r = regex.findall(url)
    url = domain + r[0]
    return url


def set_referral_url(url):
    referral = "guille21497-21"
    extra = "%26language=es_ES&keywords="
    url = "https://" + url + "?tag=" + referral + extra
    return url


def short_url(url):
    s = pyshorteners.Shortener(api_key='fde5d71c4f28a24ad80f463e45156bc8a63f87ae')
    shorturl = s.bitly.short(url)
    return shorturl


def amazon_referral(update, context, text, domain):
    user_id = update.effective_user['id']
    url = clear_url(text, domain)
    url_ref = set_referral_url(url)
    url_short = short_url(url_ref)
    scrap = scrap_amazon(url)
    title = scrap[0].strip()
    image = scrap[1]
    price = scrap[2]
    if 'NA' in title + image + price:
        msg = f"Aquí tienes el enlace de compra:\n\n🔗 {url_short}"
    else:
        msg = f"Aquí tienes el enlace de compra:\n\n🔹 *{title}*\n💰 {price}\n🔗 {url_short}"

    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="Markdown",
                            disable_web_page_preview=True,
                            text=msg)

    msg2 = f"*Recuerda:* \n 📲 Esta URL solo funciona si compras en el dispositivo donde la abres.\n 🕗 Dura 24h desde que entras al enlace. Si pasan las 24h vuelve a pinchar al enlace antes de comprar. \n 📩 Puedes copiarla y enviarla al dispositivo (PC o móvil) desde el que se realizará la commpra."
    context.bot.sendMessage(chat_id=user_id,
                        parse_mode="Markdown",
                        text=msg2)

##



def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("test", test))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, check_message))
    #dp.add_handler(MessageHandler(Filters.location, location))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://fathomless-sierra-35369.herokuapp.com/' + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
