import asyncio
import threading
import time

from flask import Flask, request

from config import WEB_HOOK_URL, APP_PORT, APP_HOST
from handlers import command_handlers, callback_handlers, handlers, db, bot, main

app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_update():
    msg_text = request.json.get('message', {}).get('text')
    print(msg_text)
    command_handler = command_handlers.get(msg_text)
    if command_handler:
        state = command_handler.get('state')
        user_id = request.json['message']['from']['id']
        cur_state = db.get_state(user_id)
        if state in {cur_state, None}:
            handler = command_handler.get('handler')
            handler()
            return "ok", 200

    if request.json.get('callback_query'):
        data = request.json['callback_query']['data']
        callback_handler = callback_handlers.get(data)
        if callback_handler:
            callback_handler()
            return "ok", 200

    user_id = None
    if request.json.get('callback_query'):
        user_id = request.json['callback_query']['from']['id']
    if request.json.get('message'):
        user_id = request.json['message']['from']['id']
    cur_state = db.get_state(user_id)
    handler = handlers.get(cur_state)

    if handler:
        handler()

    return "ok", 200


if __name__ == '__main__':
    bot.deleteWebhook()
    time.sleep(1)
    response = bot.setWebhook(WEB_HOOK_URL)

    threading.Thread(target=asyncio.run, kwargs={"main": main()}).start()

    app.run(host=APP_HOST, port=APP_PORT)
