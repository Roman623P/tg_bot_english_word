import json

import requests


class TelegramBot:
    def __init__(self, api_token):
        self.telegram_api_url = f'https://api.telegram.org/bot{api_token}'

    def deleteWebhook(self):
        requests.post(f'{self.telegram_api_url}/deleteWebhook')

    def setWebhook(self, url):
        requests.post(f'{self.telegram_api_url}/setWebhook', {"url": url})

    def sendMessage(self, chat_id, text, reply_markup=None, parse_mode=None):
        data = {
            "chat_id": chat_id,
            "text": text
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        if parse_mode:
            data["parse_mode"] = parse_mode
        requests.post(f'{self.telegram_api_url}/sendMessage', data=data)

    def deleteMessage(self, chat_id, message_id):
        data = {
            "chat_id": chat_id,
            "message_id": message_id
        }
        requests.post(f'{self.telegram_api_url}/deleteMessage', data=data)

    def setMyCommands(self, commands, scope=None):
        data = {
            "commands": json.dumps(commands)
        }
        if scope:
            data['scope'] = json.dumps(scope)
        requests.post(f'{self.telegram_api_url}/setMyCommands', data=data)

    def deleteMyCommands(self, scope=None):
        data = {}
        if scope:
            data['scope'] = json.dumps(scope)
        requests.post(f'{self.telegram_api_url}/deleteMyCommands', data=data)



