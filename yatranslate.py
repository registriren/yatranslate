from botapitamtam import BotHandler
import sqlite3
import os
import requests
import urllib
import json
import logging
import re

# from flask import Flask, request, jsonify  # для webhook

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

config = 'config.jsn'
base_url = 'https://translate.yandex.net/api/v1.5/tr.json/'
lang_all = {}
with open(config, 'r', encoding='utf-8') as c:
    conf = json.load(c)
    token = conf['access_token']
    key = conf['key']

bot = BotHandler(token)
# app = Flask(__name__)  # для webhook

if not os.path.isfile('users.db'):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE users
                      (id INTEGER PRIMARY KEY , lang TEXT)
                   """)
    conn.commit()
    c.close()
    conn.close()

conn = sqlite3.connect("users.db", check_same_thread=False)


def url_encode(txt):
    return urllib.parse.quote(txt)


def set_lang(lang, id):
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (id, lang) VALUES ({}, '{}')".format(id, lang))
        logger.info('Creating a new record for chat_id(user_id) - {}, lang - {}'.format(id, lang))
    except:
        c.execute("UPDATE users SET lang = '{}' WHERE id = {}".format(lang, id))
        logger.info('Update lang - {} for chat_id(user_id) - {}'.format(lang, id))
    conn.commit()
    c.close()
    return


def get_lang(id):
    c = conn.cursor()
    c.execute("SELECT lang FROM users WHERE id= {}".format(id))
    lang = c.fetchone()
    if lang:
        lang = lang[0]
    else:
        lang = None
    c.close()
    return lang


def translate(text, lang):
    translate_res = None
    text = url_encode(text)
    url_lang = ''.join([base_url, 'detect', '?key={}'.format(key), '&text={}'.format(text), '&hint=ru,en'])
    try:
        response = requests.get(url_lang)
        ret = response.json()
    except Exception:
        ret = None
    if lang == 'auto':
        lang_res = 'ru'
    else:
        lang_res = lang
    if ret and ret['code'] == 200:
        lang_detect = ret['lang']
        if lang == 'auto' and lang_detect == 'ru':
            lang_res = 'en'
        if lang == 'auto' and lang_detect == 'en':
            lang_res = 'ru'
        if lang_res != lang_detect:
            url = ''.join([base_url, 'translate', '?key={}'.format(key), '&text={}'.format(text),
                           '&lang={}'.format(lang_res),
                           '&format=plain'])
            response = requests.get(url)
            ret = response.json()
            translate_res = ret['text'][0]
    return translate_res


def symbol_control(TXT):
    res = True
    TXT = re.sub("(?P<url>https?://[^\s]+)", '', TXT)
    TXT = re.sub('(\r|\n)', '', TXT)
    TXT = re.sub('[^A-Za-zА-Яа-я ]', '', TXT)
    TXT = re.sub('^ ', '', TXT)
    TXT = re.sub(' +', ' ', TXT)
    TXT = re.sub(' *$', '', TXT)
    if len(TXT) < 2:
        res = False
    return res


# @app.route('/', methods=['POST'])  # для webhook
def main():
    res_len = 0
    while True:
        last_update = bot.get_updates()
        # last_update = request.get_json()  # для webhook
        if last_update:
            chat_id = bot.get_chat_id(last_update)
            type_upd = bot.get_update_type(last_update)
            text = bot.get_text(last_update)
            payload = bot.get_payload(last_update)
            mid = bot.get_message_id(last_update)
            callback_id = bot.get_callback_id(last_update)
            name = bot.get_name(last_update)
            admins = bot.get_chat_admins(chat_id)
            att_type = bot.get_attach_type(last_update)
            if att_type == 'share':
                text = None
            if not admins or admins and name in [i['name'] for i in admins['members']]:
                if text == '/lang' or text == '@yatranslate /lang':
                    buttons = [[{"type": 'callback',
                                 "text": 'Авто|Auto',
                                 "payload": 'auto'},
                                {"type": 'callback',
                                 "text": 'Русский',
                                 "payload": 'ru'},
                                {"type": 'callback',
                                 "text": 'English',
                                 "payload": 'en'}]]
                    bot.send_buttons('Направление перевода\nTranslation direction', buttons,
                                     chat_id)  # вызываем три кнопки с одним описанием
                    text = None
                if text == '/lang ru' or text == '@yatranslate /lang ru':
                    set_lang('ru', chat_id)
                    bot.send_message('Текст будет переводиться на Русский', chat_id)
                    text = None
                if text == '/lang en' or text == '@yatranslate /lang en':
                    set_lang('en', chat_id)
                    bot.send_message('Text will be translated into English', chat_id)
                    text = None
                if text == '/lang auto' or text == '@yatranslate /lang auto':
                    set_lang('auto', chat_id)
                    bot.send_message('Русский|English - автоматически|automatically', chat_id)
                    text = None
                if payload:
                    set_lang(payload, chat_id)
                    lang = get_lang(chat_id)
                    text = None
                    if lang == 'ru':
                        bot.send_answer_callback(callback_id, 'Текст будет переводиться на Русский')
                        bot.delete_message(mid)
                    elif lang == 'auto':
                        bot.send_answer_callback(callback_id, 'Русский|English - автоматически|automatically')
                        bot.delete_message(mid)
                    else:
                        bot.send_answer_callback(callback_id, 'Text will be translated into English')
                        bot.delete_message(mid)

            if type_upd == 'bot_started':
                bot.send_message(
                    'Отправьте или перешлите боту текст. Язык переводимого текста определяется автоматически. '
                    'Перевод по умолчанию на русский. Для изменения направления перевода используйте команду /lang\n'
                    'Send or forward bot text. The language of the translated text is determined automatically. The '
                    'default translation into Russian. To change the translation direction, use the command /lang',
                    chat_id)
                set_lang('auto', chat_id)
                text = None
            if chat_id:
                lang = get_lang(chat_id)
                if not lang and '-' in str(chat_id):
                    lang = 'ru'
                    set_lang('ru', chat_id)
                elif not lang:
                    lang = 'auto'
                    set_lang('auto', chat_id)
            else:
                lang = 'auto'
            if type_upd == 'message_construction_request':
                text_const = bot.get_construct_text(last_update)
                sid = bot.get_session_id(last_update)
                if text_const:
                    translt = translate(text_const, 'auto')
                    if translt:
                        bot.send_construct_message(sid, hint=None, text=translt)
                    else:
                        bot.send_construct_message(sid, 'Введите текст для перевода и отправки в чат | '
                                                        'Enter the text to be translated and send to the chat')
                else:
                    bot.send_construct_message(sid, 'Введите текст для перевода и отправки в чат | '
                                                    'Enter the text to be translated and send to the chat')
            elif text and symbol_control(text):
                translt = translate(text, lang)
                if translt:
                    len_sym = len(translt)
                    res_len += len_sym
                    logger.info('chat_id: {}, len symbols: {}, result {}'.format(chat_id, len_sym, res_len))
                    if res_len >> 10000000:  # контроль в логах количества переведенных символов
                        res_len = 0
                    if '-' in str(chat_id):
                        bot.send_reply_message(translt, mid, chat_id)
                    else:
                        bot.send_message(translt, chat_id)
        # return jsonify(last_update)  # для webhook


# if __name__ == '__main__':  # для webhook
#    try:
#        app.run(port=29347, host="0.0.0.0")
#    except KeyboardInterrupt:
#        exit()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
