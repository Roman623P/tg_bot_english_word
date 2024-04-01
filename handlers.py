import asyncio
import datetime
import json
import random

from flask import request

from config import API_TOKEN, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from TelegramBotAPI import TelegramBot
from Database import Database

from keyboards_menu import *
from states import States

bot = TelegramBot(API_TOKEN)

db = Database(db_user=DB_USER, db_password=DB_PASSWORD, db_host=DB_HOST, db_port=DB_PORT, db_name=DB_NAME)


# Напоминание
async def main():
    while True:
        await reminder()
        await asyncio.sleep(60)


async def reminder():
    users = db.get_all_users_to_send_reminder(2)
    if users is None:
        return

    for user in users:
        user_id = user[0]
        chat_id = user[0]
        text = "🔔 Пора пройти тест!"
        reply_markup = reminder_inline_keyboard_markup
        bot.sendMessage(chat_id, text, reply_markup)

        db.set_is_reminder_send(user_id, True)


# Основа бота
def start():
    chat_id = request.json['message']['chat']['id']
    user_id = request.json['message']['from']['id']
    print(user_id)
    print(chat_id)
    if not db.get_user_by_id(user_id):
        db.add_user(user_id)

    text = "Привет! 👋 Я чат-бот для изучения английских слов."
    reply_markup = start_reply_keyboard_markup
    bot.sendMessage(chat_id, text, reply_markup)

    db.set_state(user_id=user_id, state=States.DEFAULT)
    db.clear_test(user_id)
    db.set_is_reminder_send(user_id, False)


def startTest():
    if request.json.get('callback_query'):
        chat_id = request.json['callback_query']['message']['chat']['id']
        user_id = request.json['callback_query']['from']['id']
        message_id = request.json['callback_query']['message']['message_id']

        bot.deleteMessage(chat_id, message_id)
    else:
        chat_id = request.json['message']['chat']['id']
        user_id = request.json['message']['from']['id']

    text = "🔄 Подбор вопросов для теста..."
    bot.sendMessage(chat_id, text)

    questions_number = genQuestions(user_id)

    if questions_number == 0:
        text = ("❌ Не удалось подобрать вопросы.\n"
                "Попробуйте выбрать другую тему или подождать.")
        bot.sendMessage(chat_id, text)

        return

    text = (f"<b>Всего вопросов в тесте:</b> {questions_number}\n\n"
            f"Удачи!")
    reply_markup = startTest_reply_keyboard_markup
    bot.sendMessage(chat_id, text, reply_markup, parse_mode='HTML')

    newQuestion(chat_id, user_id)

    db.set_state(user_id=user_id, state=States.TEST_STATE)


def genQuestions(user_id):
    # Кол-во вопросов в тесте
    questions_number = 0
    # Получение параметра пользователя с максимальным кол-вом вопросов в тесте
    max_questions_number = db.get_user_questions_number(user_id)
    # Получение слов заданной всех слов заданной темы
    all_words = db.get_words_for_questions(user_id)

    # Список выученных слов
    learned_words = []

    # Если нет слов для теста
    if len(all_words) == 0:
        return questions_number

    # Получение кривой забывания из json-файла
    with open('config.json', 'r') as file:
        conf_file = json.load(file)

    # Подбор слов для теста
    for word_id, correct_answers_number, last_repeat in all_words:
        interval = 0
        # Если слово уже изучалось
        if correct_answers_number is not None:
            interval = conf_file.get(f"{correct_answers_number}")
        # Если слово вышло за кривую забывания (выучено)
        if interval is None:
            learned_words.append(word_id)
            continue

        # Если ещё не пришло время для повторения
        if last_repeat is not None and datetime.datetime.now()-last_repeat < datetime.timedelta(minutes=interval):
            continue

        # Иначе добавляем слово в список вопросов для теста
        db.add_word_in_test(user_id, word_id)

        questions_number += 1

        # Если необходимое кол-во слов подобрано
        if questions_number >= max_questions_number:
            break

    # Если слов не хватает,
    # то добираем из числа изученных
    if questions_number < max_questions_number:
        missing_words = random.sample(learned_words, min(len(learned_words), max_questions_number-questions_number))
        for word_id in missing_words:
            db.add_word_in_test(user_id, word_id)

            questions_number += 1

    return questions_number


def testing():
    if not request.json.get('callback_query'):
        return

    chat_id = request.json['callback_query']['message']['chat']['id']
    message_id = request.json['callback_query']['message']['message_id']
    user_id = request.json['callback_query']['from']['id']
    user_answer = request.json['callback_query']['data']

    user_answer_word_id, user_answer_word_translation = user_answer.split(',')
    user_answer_word_translation = user_answer_word_translation.lstrip()
    
    bot.deleteMessage(chat_id, message_id)

    word_obj = db.get_word_by_id_from_test(user_id, user_answer_word_id)
    if word_obj is None:
        return

    word_id, word, word_translation = db.get_word_by_id_from_test(user_id, user_answer_word_id)

    if user_answer_word_translation == word_translation:
        text = (f"Ваш ответ: <b>{user_answer_word_translation}</b>\n"
                f"✅ Правильно")
        bot.sendMessage(chat_id, text, parse_mode='HTML')

        word_correct_answers_number = db.get_correct_answers_number_from_learning(user_id, word_id)
        if word_correct_answers_number is None:
            db.add_learning(user_id, word_id, 1)
        else:
            db.update_learning(user_id, word_id, word_correct_answers_number + 1)

        db.set_is_right_in_test(user_id, word_id, True)
    else:
        text = (f"Ваш ответ: <b>{user_answer_word_translation}</b>\n"
                f"❌ Неправильно\n\n"
                f"Правильный ответ:\n"
                f"<tg-spoiler><b>{word_translation}</b></tg-spoiler>")
        bot.sendMessage(chat_id=chat_id, text=text, parse_mode='HTML')

        word_correct_answers_number = db.get_correct_answers_number_from_learning(user_id, word_id)
        if word_correct_answers_number is None:
            db.add_learning(user_id, word_id, 0)
        else:
            db.update_learning(user_id, word_id, 0)

        db.set_is_right_in_test(user_id, word_id, False)

    newQuestion(chat_id, user_id)


def newQuestion(chat_id, user_id):
    word_obj = db.get_word_from_test(user_id)
    if word_obj is None:
        finishTest()
        return
    word_id, word, word_translation = word_obj
    fakeAnswers = db.get_fake_words_for_question(word_id)

    answers = [word_translation, *fakeAnswers]
    random.shuffle(answers)
    text = f"Как переводится слово <b>{word}</b>?"
    inline_keyboard = [{"text": f"{answer}", "callback_data": f"{word_id}, {answer}"} for answer in answers]
    reply_markup = {
        "inline_keyboard": [inline_keyboard[i:i + 2] for i in range(0, len(answers), 2)]
    }
    bot.sendMessage(chat_id, text, reply_markup, parse_mode='HTML')


def finishTest():
    if request.json.get('callback_query'):
        chat_id = request.json['callback_query']['message']['chat']['id']
        user_id = request.json['callback_query']['from']['id']
    else:
        chat_id = request.json['message']['chat']['id']
        user_id = request.json['message']['from']['id']

    text = "Тест завершен 🎉"
    reply_markup = start_reply_keyboard_markup
    bot.sendMessage(chat_id, text, reply_markup)

    testStatistic(chat_id, user_id)

    db.set_state(user_id=user_id, state=States.DEFAULT)
    db.clear_test(user_id)
    db.set_user_last_repeat(user_id)
    db.set_is_reminder_send(user_id, False)


def testStatistic(chat_id, user_id):
    grouped_words = dict(db.get_is_right_grouped_words(user_id))

    text = (f"<b>Правильные ответы</b> - {grouped_words.get(True, 0)}\n"
            f"<b>Неправильные ответы</b> - {grouped_words.get(False, 0)}\n"
            f"<b>Без ответа</b> - {grouped_words.get(None, 0)}\n\n"
            f"<b>Всего вопросов</b> - {sum(grouped_words.values())}")
    bot.sendMessage(chat_id, text, parse_mode='HTML')


def usageExample():
    chat_id = request.json['message']['chat']['id']
    user_id = request.json['message']['from']['id']

    usageExamples = db.get_word_usage_example_from_test(user_id)

    text = (f"<b>Пример использования на английском языке:</b>\n"
            f"\"{usageExamples[0] or '-'}\"\n\n"
            f"<b>Пример использования на русском языке:</b>\n"
            f"<tg-spoiler>\"{usageExamples[1] or '-' }\"</tg-spoiler>")
    bot.sendMessage(chat_id=chat_id, text=text, parse_mode="HTML")


def statictics():
    chat_id = request.json['message']['chat']['id']
    user_id = request.json['message']['from']['id']

    learned_word_number = db.get_learned_word_number(user_id)
    word_number_in_topic = db.get_word_number_in_topic(user_id)
    user_last_repeat = db.get_user_last_repeat(user_id)

    text = (f"<b>Статистика пользователя</b>\n\n"
            f"<b>Выучено слов:</b> {learned_word_number or 0}\n"
            f"<b>Количество слов в выбранной теме:</b> {word_number_in_topic or 0}\n"
            f"<b>Последнее прохождение теста:</b>\n{user_last_repeat and user_last_repeat.strftime('%H:%M   %d.%m.%Y') or '-'}")
    bot.sendMessage(chat_id=chat_id, text=text, parse_mode="HTML")


def paramsSetting():
    chat_id = request.json['message']['chat']['id']

    reply_markup = menu_reply_keyboard_markup
    text = "Настройка параметров теста. Настройка производится через меню ↙"
    bot.sendMessage(chat_id, text, reply_markup)


def backToMain():
    chat_id = request.json['message']['chat']['id']
    user_id = request.json['message']['from']['id']

    text = "🏠 Главная. Что вы хотите сделать?"
    reply_markup = start_reply_keyboard_markup
    bot.sendMessage(chat_id, text, reply_markup)

    db.set_state(user_id=user_id, state=States.DEFAULT)


def setTopic():
    
    chat_id = request.json['message']['chat']['id']
    user_id = request.json['message']['from']['id']

    title, description = db.get_user_topic(user_id)

    text = (f"Выбор темы для изучения.\n\n"
            f"<b>Текущая тема:</b> {title}\n"
            f"<b>Описание:</b> {description}")
    reply_markup = setTopic_reply_keyboard
    bot.sendMessage(chat_id, text, reply_markup, parse_mode='HTML')

    topics = db.get_topics()
    text = f"Выберите тему из предложенных:"
    inline_keyboard = [{"text": f"{title}", "callback_data": f"{topic_id}"} for topic_id, title in topics]
    reply_markup = {
        "inline_keyboard": [inline_keyboard[i:i+2] for i in range(0, len(topics), 2)]
    }
    bot.sendMessage(chat_id, text, reply_markup)

    db.set_state(user_id=user_id, state=States.GET_TOPIC)


def getTopic():
    if not request.json.get('callback_query'):
        chat_id = request.json['message']['chat']['id']
        bot.sendMessage(chat_id, "Выберите тему для изучения!")
        return

    chat_id = request.json['callback_query']['message']['chat']['id']
    message_id = request.json['callback_query']['message']['message_id']
    user_id = request.json['callback_query']['from']['id']
    topic_id = request.json['callback_query']['data']

    bot.deleteMessage(chat_id, message_id)

    db.set_user_topic(user_id, topic_id)
    db.set_state(user_id=user_id, state=States.DEFAULT)

    title, description = db.get_user_topic(user_id)
    text = (f"<b>Новая тема:</b> {title}\n"
            f"<b>Описание:</b> {description}")
    reply_markup = start_reply_keyboard_markup
    bot.sendMessage(chat_id, text, reply_markup, parse_mode='HTML')


def setQuestionsNumber():
    chat_id = request.json['message']['chat']['id']
    user_id = request.json['message']['from']['id']

    questions_number = db.get_user_questions_number(user_id)

    text = (f"Настройка количества слов в тесте.\n\n"
            f"<b>Текущее значение:</b> {questions_number}\n\n"
            f"Отправьте новое значение в сообщении.")
    reply_markup = setQuestionsNumber_reply_keyboard_markup
    bot.sendMessage(chat_id, text, reply_markup, parse_mode='HTML')

    db.set_state(user_id=user_id, state=States.GET_QUESTIONS_NUMBER)


def getQuestionsNumber():
    if not request.json.get('message'):
        chat_id = request.json['callback_query']['message']['chat']['id']
        bot.sendMessage(chat_id, "Введите количество вопросов!")
        return

    chat_id = request.json['message']['chat']['id']
    user_id = request.json['message']['from']['id']
    questions_number = request.json['message']['text']

    if not questions_number.isdigit():
        bot.sendMessage(chat_id, "Введенное значение не является числом!")
        return

    db.set_user_questions_number(user_id, int(questions_number))
    db.set_state(user_id=user_id, state=States.DEFAULT)

    questions_number = db.get_user_questions_number(user_id)
    text = f"<b>Новое количество вопросов:</b> {questions_number}\n"
    reply_markup = start_reply_keyboard_markup
    bot.sendMessage(chat_id, text, reply_markup, parse_mode='HTML')


def setCorrectAnswersNumber():
    chat_id = request.json['message']['chat']['id']
    user_id = request.json['message']['from']['id']

    correct_answers_number = db.get_user_correct_answers_number(user_id)

    text = (f"Настройка количества правильных ответов для того, чтобы слово считалось выученным.\n\n"
            f"<b>Текущее значение:</b> {correct_answers_number}\n\n"
            f"Отправьте новое значение в сообщении.")
    reply_markup = setCorrectAnswersNumber_reply_keyboard_markup
    bot.sendMessage(chat_id, text, reply_markup, parse_mode='HTML')

    db.set_state(user_id=user_id, state=States.GET_CORRECT_ANSWERS_NUMBER)


def getCorrectAnswersNumber():
    if not request.json.get('message'):
        chat_id = request.json['callback_query']['message']['chat']['id']
        bot.sendMessage(chat_id, "Введите количество правильных ответов!")
        return

    chat_id = request.json['message']['chat']['id']
    user_id = request.json['message']['from']['id']
    correct_answers_number = request.json['message']['text']

    if not correct_answers_number.isdigit():
        bot.sendMessage(chat_id, "Введенное значение не является числом!")
        return

    db.set_user_correct_answers_number(user_id, int(correct_answers_number))
    db.set_state(user_id=user_id, state=States.DEFAULT)

    correct_answers_number = db.get_user_correct_answers_number(user_id)
    text = f"<b>Новое количество правильных ответов для того, чтобы слово считалось выученным:</b> {correct_answers_number}\n"
    reply_markup = start_reply_keyboard_markup
    bot.sendMessage(chat_id, text, reply_markup, parse_mode='HTML')


def deferReminder():
    chat_id = request.json['callback_query']['message']['chat']['id']
    message_id = request.json['callback_query']['message']['message_id']
    user_id = request.json['callback_query']['from']['id']

    bot.deleteMessage(chat_id, message_id)

    db.set_user_last_repeat(user_id)
    db.set_is_reminder_send(user_id, False)


command_handlers = {
    '/start': {'handler': start},
    'Давайте начнем тест.': {'handler': startTest, 'state': States.DEFAULT},
    'Посмотреть статистику': {'handler': statictics, 'state': States.DEFAULT},
    'Настроить параметры': {'handler': paramsSetting, 'state': States.DEFAULT},
    'Досрочно завершить тест': {'handler': finishTest, 'state': States.TEST_STATE},
    'Пример использования': {'handler': usageExample, 'state': States.TEST_STATE},
    'Выбрать тему': {'handler': setTopic, 'state': States.DEFAULT},
    'Отменить настройку темы': {'handler': backToMain, 'state': States.GET_TOPIC},
    'Количество вопросов': {'handler': setQuestionsNumber, 'state': States.DEFAULT},
    'Отменить настройку количества вопросов': {'handler': backToMain, 'state': States.GET_QUESTIONS_NUMBER},
    'Количество правильных ответов': {'handler': setCorrectAnswersNumber, 'state': States.DEFAULT},
    'Отменить настройку количества правильных ответов': {'handler': backToMain, 'state': States.GET_CORRECT_ANSWERS_NUMBER},
}

callback_handlers = {
    'Пройти тест': startTest,
    'Отложить напоминание на 30 мин.': deferReminder
}

handlers = {
    States.GET_TOPIC: getTopic,
    States.GET_QUESTIONS_NUMBER: getQuestionsNumber,
    States.GET_CORRECT_ANSWERS_NUMBER: getCorrectAnswersNumber,
    States.TEST_STATE: testing
}
