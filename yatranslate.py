from botapitamtam import BotHandler
import requests
import urllib
import json
import logging

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


def url_encode(txt):
    return urllib.parse.quote(txt)


def main():
    res_len = 0
    marker = None
    while True:
        update = bot.get_updates(marker)
        if update is None:  # проверка на пустое событие, если пусто - возврат к началу цикла
            continue
        marker = bot.get_marker(update)
        updates = update['updates']
        for last_update in list(updates):  # формируем цикл на случай если updates вернул список из нескольких событий
            type_upd = bot.get_update_type(last_update)
            text = bot.get_text(last_update)
            chat_id = bot.get_chat_id(last_update)
            payload = bot.get_payload(last_update)
            if text == '/lang':
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
            if text == '/lang ru':
                lang_all.update({chat_id: 'ru'})
                bot.send_message('Текст будет переводиться на Русский', chat_id)
                text = None
            if text == '/lang en':
                lang_all.update({chat_id: 'en'})
                bot.send_message('Text will be translated into English', chat_id)
                text = None
            if text == '/lang auto':
                lang_all.update({chat_id: 'auto'})
                bot.send_message('Русский|English - автоматически|automatically', chat_id)
                text = None
            if payload is not None:
                print(lang_all)
                lang_all.update({chat_id: payload})
                print(lang_all)
                lang = lang_all.get(chat_id)
                text = None
                if lang == 'ru':
                    bot.send_message('______\nТекст будет переводиться на Русский', chat_id)
                elif lang == 'auto':
                    bot.send_message('______\nРусский|English - автоматически|automatically', chat_id)
                else:
                    bot.send_message('______\nText will be translated into English', chat_id)
            if type_upd == 'bot_started':
                bot.send_message(
                    'Отправьте или перешлите боту текст. Язык переводимого текста определяется автоматически. '
                    'Перевод по умолчанию на русский. Для изменения направления перевода используйте команду /lang',
                    chat_id)
                lang_all.update({chat_id: 'ru'})
                text = None
            if chat_id in lang_all.keys():
                lang = lang_all.get(chat_id)
            else:
                lang = 'ru'
            if text is not None:
                text = url_encode(text)
                url_lang = ''.join([base_url, 'detect', '?key={}'.format(key), '&text={}'.format(text), '&hint=ru,en'])
                response = requests.get(url_lang)
                ret = response.json()
                if lang == 'auto':
                    lang_res = 'ru'
                else:
                    lang_res = lang
                if ret['code'] == 200:
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
                        translate = ret['text'][0]
                        len_sym = len(translate)
                        res_len += len_sym
                        logger.info('chat_id: {}, len symbols: {}, result {}'.format(chat_id, len_sym, res_len))
                        if res_len >> 10000000:  # контроль в логах количества переведенных символов
                            res_len = 0
                        bot.send_message(translate, chat_id)
                # else:
                #    bot.send_message('Перевод невозможен\nTranslation not available', chat_id)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
