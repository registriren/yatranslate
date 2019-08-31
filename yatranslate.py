from botapitamtam import BotHandler
import requests
import urllib
import json
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

config = 'config.json'
base_url = 'https://translate.yandex.net/api/v1.5/tr.json/'
lang_all = {}
with open(config, 'r', encoding='utf-8') as c:
    conf = json.load(c)
    token = conf['access_token']
    key = conf['key']

bot = BotHandler(token)

def urlencode(str):
  return urllib.parse.quote(str)

def main():
    marker = None
    while True:
        last_update = bot.get_updates(marker)
        if last_update == None: #проверка на пустое событие, если пусто - возврат к началу цикла
            continue
        marker = bot.get_marker(last_update)
        type_upd = bot.get_update_type(last_update)
        text = bot.get_text(last_update)
        chat_id = bot.get_chat_id(last_update)
        payload = bot.get_payload(last_update)
        if text == '/lang':
            buttons = [[{"type": 'callback',
                        "text": 'Русский',
                        "payload": 'ru'},
                       {"type": 'callback',
                        "text": 'English',
                        "payload": 'en'}]]
            bot.send_buttons('Направление перевода', buttons, chat_id) #вызываем две кнопки с одним описанием
            text = None
        if text == '/lang ru':
            lang_all.update({chat_id : 'ru'})
            bot.send_message('Текст будет переводиться на Русский', chat_id)
            text = None
        if text == '/lang en':
            lang_all.update({chat_id : 'en'})
            bot.send_message('Текст будет переводиться на English', chat_id)
            text = None    
        if payload != None:
            print(lang_all)
            lang_all.update({chat_id : payload})
            print(lang_all)
            lang = lang_all.get(chat_id)
            text = None
            if lang == 'ru':
                   bot.send_message('______\nТекст будет переводиться на Русский', chat_id)
            else:
                   bot.send_message('______\nТекст будет переводиться на English', chat_id)
        if type_upd == 'bot_started':
             bot.send_message('Отправте или перешлите боту текст. Язык переводимого текста определяется автоматически. '
                             'Перевод по умолчанию на русский. Для изменения направления перевода используйте команду /lang', chat_id)
             lang_all.update({chat_id : 'ru'})
             text = None
        if chat_id in lang_all.keys():
            lang = lang_all.get(chat_id)
        else:
            lang = 'ru'
        if text != None:
               text = urlencode(text)
               url_lang = ''.join([base_url, 'detect', '?key={}'.format(key), '&text={}'.format(text), '&hint=ru,en'])
               response = requests.get(url_lang)
               ret = response.json()
               lang_detect = ret['lang']
               if lang_detect == 'ru':
                   lang = 'en'
               if lang_detect == 'en':
                   lang = 'ru'
               url = ''.join([base_url, 'translate', '?key={}'.format(key), '&text={}'.format(text), '&lang={}'.format(lang), '&format=plain'])
               response = requests.get(url)
               ret = response.json()
               translate = ret['text'][0]
               bot.send_message('{}\n_____\nПереведено сервисом «Яндекс.Переводчик»'.format(translate), chat_id)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
