import logging
import os

import telegram
import json
import re
import requests
import pyshorteners
import validators
import regex
import urlextract

from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from validators import ValidationFailure
from urlextract import URLExtract

from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Tokens and IDs
BOT_TOKEN = '5770033505:AAH3DVUupmvneAzrfOXGjd1S8lhQFFOPj60'
BITLY_TOKEN = 'fde5d71c4f28a24ad80f463e45156bc8a63f87ae'
ID_AMAZON_REFERRAL = "guille21497-21"

## COMMANDS ##

def start(update, context):
    name = update.effective_user['first_name']
    user_id = update.effective_user['id']
    url_short = short_url('https://www.amazon.es/?&_encoding=UTF8&tag=guille21497-21&linkCode=ur2&linkId=8e9bc8f12992fadb5454eb4c85dc0d0c&camp=3638&creative=24630')
    msg = f"*Introduce una URL de un producto de Amazon y te la devolveré con mi referido* 💰 \n\n URL general de Amazon: \n🔗 {url_short}"
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="Markdown",
                            disable_web_page_preview=True,
                            text=msg)
    msg2 = f"*Recuerda:* \n 📲 Esta URL solo funcionará si compras desde el dispositivo donde la abres.\n 🕗 Dura 24h desde que entras al enlace. _(si pasan las 24h vuelve a pinchar al enlace antes de comprar)_ \n 📩 Puedes copiarla y enviarla al dispositivo (PC, móvil o tablet) desde el que se realizará la compra."
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
    print("TEST \n")
    name = update.effective_user['first_name']
    user_id = update.effective_user['id']
    uri = "amzn.eu/d/c1y73vs"
    ht = "https://"
    tal = is_string_an_url(uri)

    ext1 = "https://www.amazon.es/SanDisk-Professional-Compartimentos-conectividad-Thunderbolt/dp/B09JGQW5XS/?_encoding=UTF8&pd_rd_w=exCvH&content-id=amzn1.sym.e938e71b-2a18-43eb-855b-f4edce2ba725&pf_rd_p=e938e71b-2a18-43eb-855b-f4edce2ba725&pf_rd_r=6CJKTVWJWEN1AAAGANRW&pd_rd_wg=F2JuO&pd_rd_r=c079595d-f687-40e7-a59e-df343f8f776f&ref_=pd_gw_ci_mcx_mr_hp_atf_m&th=1"
    ext2 = "sdadasd https://pypi.org/project/regex/2022.9.13/ dsadasdsas"
    ext3 = "dasdas amzn.eu/d/c1y73vs  dasdas"
    ext4 = "dasdadasdas"
    
    link_regex = re.compile("((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)", re.DOTALL)
    links = re.findall(link_regex, ext1)
    print(links)

    extractor = URLExtract()
    urls = extractor.find_urls(ext1)
    print(urls)
    print(urls[0])

    tal2 = re.search("(?P<url>https?://[^\s]+)", ext1).group("url")
    print(tal2)
                      
    # if is_string_an_url(uri):
    #     r = requests.get(uri)
    #     context.bot.sendMessage(chat_id=user_id,
    #                         parse_mode="Markdown",
    #                         text=r.url)
    # elif is_string_an_url(ht+uri):
    #     r = requests.get(ht+uri)
    #     context.bot.sendMessage(chat_id=user_id,
    #                         parse_mode="Markdown",
    #                         text=r.url)
    # else:
    #     msg = f"*TEST*"
    #     context.bot.sendMessage(chat_id=user_id,
    #                             parse_mode="Markdown",
    #                             text=msg)

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

## AMAZON ##

def check_message(update, context):
    ht = "https://"
    name = update.effective_user['first_name']
    user_id = update.effective_user['id']

    text = update.message.text
    logger.info(f"{name} sent a msg: {text}")

    extractor = URLExtract()
    urls = extractor.find_urls(text)
    if len(urls) > 0:
        text = urls[0]
    print("- Text: " + text)

    text_s = text.strip()
    domain = "{0.netloc}".format(urlsplit(text_s))
    print("- Domain: " + domain)

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
                url_incorrecta(update, context, 0)
        elif is_string_an_url(ht+text):
            r = requests.get(ht+text)
            text_3 = r.url
            text_3s = text_3.strip()
            domain_3 = "{0.netloc}".format(urlsplit(text_3s))
            if domain_3.find("amazon.") != -1:
                amazon_referral(update, context, text_3s, domain_3)
            else:
                url_incorrecta(update, context, 0)
        else:
            url_incorrecta(update, context, 0)


def url_incorrecta(update, context, produ):
    name = update.effective_user['first_name']
    user_id = update.effective_user['id']

    if produ == 1:
        msg = f"No detecto ningún producto de Amazon en esa URL \n "
    else:
        msg = f"El mensaje no contiene ninguna URL de Amazon \n "
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="Markdown",
                            text=msg)
    url_short = short_url("https://www.amazon.es/?&_encoding=UTF8&tag=guille21497-21&linkCode=ur2&linkId=8e9bc8f12992fadb5454eb4c85dc0d0c&camp=3638&creative=24630")
    msg = f"Puedes usar la siguiente URL general de Amazon: \n\n🔗 {url_short}"
    context.bot.sendMessage(chat_id=user_id,
                                parse_mode="Markdown",
                                disable_web_page_preview=True,
                                text=msg)
    msg2 = f"*Recuerda:* \n 📲 Esta URL solo funcionará si compras desde el dispositivo donde la abres.\n 🕗 Dura 24h desde que entras al enlace. _(si pasan las 24h vuelve a pinchar al enlace antes de comprar)_ \n 📩 Puedes copiarla y enviarla al dispositivo (PC, móvil o tablet) desde el que se realizará la compra."
    context.bot.sendMessage(chat_id=user_id,
                                parse_mode="Markdown",
                                text=msg2)


def amazon_referral(update, context, text, domain):
    user_id = update.effective_user['id']
    url = clear_url(text, domain, update, context,)
    url_ref = set_referral_url(url)
    url_short = short_url(url_ref)

    # scrap = scrap_amazon(url)
    # title = scrap[0].strip()
    # image = scrap[1]
    # price = scrap[2]
    # if 'NA' in title + image + price:
    #     msg = f"Aquí tienes el enlace de compra:\n\n🔗 {url_short}"
    # else:
    #     msg = f"Aquí tienes el enlace de compra:\n\n🔹 *{title}*\n💰 {price}\n🔗 {url_short}"

    msg = f"Aquí tienes el enlace de compra:\n\n🔗 {url_short}"
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="Markdown",
                            disable_web_page_preview=True,
                            text=msg)

    msg2 = f"*Recuerda:* \n 📲 Esta URL solo funciona si compras en el dispositivo donde la abres.\n 🕗 Dura 24h desde que entras al enlace. Si pasan las 24h vuelve a pinchar al enlace antes de comprar. \n 📩 Puedes copiarla y enviarla al dispositivo (PC o móvil) desde el que se realizará la compra."
    context.bot.sendMessage(chat_id=user_id,
                        parse_mode="Markdown",
                        text=msg2)


def clear_url(url, domain, update, context):
    regex = re.compile("(/[dg]p/[^/?]+)")
    r = regex.findall(url)
    if len(r) > 0:
        url = domain + r[0]
    else:
        url_incorrecta(update, context, 1)
    return url


def set_referral_url(url):
    extra = "%26language=es_ES&keywords="
    url = "https://" + url + "?tag=" + ID_AMAZON_REFERRAL + extra
    return url


def short_url(url):
    s = pyshorteners.Shortener(api_key=BITLY_TOKEN)
    shorturl = s.bitly.short(url)
    return shorturl


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


def is_string_an_url(url_string: str) -> bool:
    result = validators.url(url_string)
    if isinstance(result, ValidationFailure):
        return False

    return result


## MAIN ##

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(BOT_TOKEN, use_context=True)

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
                          url_path=BOT_TOKEN)
    updater.bot.setWebhook('https://fathomless-sierra-35369.herokuapp.com/' + BOT_TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()