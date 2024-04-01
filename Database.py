import datetime
from typing import Any

import psycopg2
from psycopg2 import Error


class Database:
    def __init__(self, db_user: str, db_password: str, db_host: str, db_port: str, db_name: str):
        try:
            self.connection = psycopg2.connect(
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
                database=db_name
            )
            self.cursor = self.connection.cursor()

        except(Exception, Error) as error:
            print("Ошибка при работе с БД. ", error)

    def __del__(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.connection is not None:
            self.connection.close()

    def add_user(self, user_id: int):
        try:
            self.cursor.execute(f"SELECT id FROM topics WHERE user_id IS NULL")
            topic = self.cursor.fetchone()
            print(topic)
            topic_id = None
            if topic:
                topic_id = topic[0]
            
            query = (f"INSERT INTO users (id, topic_id, questions_number, correct_answers_number) "
                     f"VALUES (%(user_id)s, %(topic_id)s, %(questions_number)s, %(correct_answers_number)s)")
            print(query)
            data = {
                "user_id": user_id,
                "topic_id": topic_id,
                "questions_number": 5,
                "correct_answers_number": 5,
            }
            print(data)
            self.cursor.execute(query, data)
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при добавлении пользователя.", error)

    def get_user_by_id(self, user_id: int) -> tuple[Any, ...] | None:
        try:
            query = f"SELECT * FROM users WHERE id = %(user_id)s"
            data = {"user_id": user_id}
            self.cursor.execute(query, data)
            return self.cursor.fetchone()
        except (Exception, Error) as error:
            print("Ошибка при получении пользователя по id.", error)
            print("\nОшибка тут")

    def set_state(self, user_id: int, state: int = 0):
        try:
            query = (f"UPDATE users "
                     f"SET state = COALESCE(%(state)s, state)"
                     f"WHERE id = %(user_id)s")
            data = {
                "user_id": user_id,
                "state": state
            }
            self.cursor.execute(query, data)
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при обновлении состояния бота пользователя.", error)

    def get_state(self, user_id: int) -> int | None:
        try:
            query = f"SELECT state FROM users WHERE id = %(user_id)s"
            data = {"user_id": user_id}
            self.cursor.execute(query, data)
            res = self.cursor.fetchone()
            if res is None:
                return None
            return res[0]
        except (Exception, Error) as error:
            print("Ошибка при получении состояния бота пользователя по id.", error)

    def set_user_topic(self, user_id: int, topic_id: int):
        try:
            query = (f"UPDATE users "
                     f"SET topic_id = COALESCE(%(topic_id)s, topic_id)"
                     f"WHERE id = %(user_id)s")
            data = {
                "user_id": user_id,
                "topic_id": topic_id
            }
            self.cursor.execute(query, data)
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при обновлении темы теста пользователя.", error)

    def get_user_topic(self, user_id: int) -> tuple[Any, ...]:
        try:
            query = f"SELECT title, description FROM users JOIN topics ON users.topic_id = topics.id WHERE users.id = %(user_id)s"
            data = {"user_id": user_id}
            self.cursor.execute(query, data)
            return self.cursor.fetchone()
        except (Exception, Error) as error:
            print("Ошибка при получении темы теста пользователя.", error)

    def get_topics(self) -> list[tuple[Any, ...]]:
        try:
            query = f"SELECT id, title FROM topics"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except (Exception, Error) as error:
            print("Ошибка при получении темы теста пользователя.", error)

    def set_user_questions_number(self, user_id: int, questions_number: int):
        try:
            query = (f"UPDATE users "
                     f"SET questions_number = COALESCE(%(questions_number)s, questions_number)"
                     f"WHERE id = %(user_id)s")
            data = {
                "user_id": user_id,
                "questions_number": questions_number
            }
            self.cursor.execute(query, data)
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при обновлении темы теста пользователя.", error)

    def get_user_questions_number(self, user_id: int) -> int:
        try:
            query = f"SELECT questions_number FROM users WHERE users.id = %(user_id)s"
            data = {"user_id": user_id}
            self.cursor.execute(query, data)
            res = self.cursor.fetchone()
            return res[0]
        except (Exception, Error) as error:
            print("Ошибка при получении темы теста пользователя.", error)

    def set_user_correct_answers_number(self, user_id: int, correct_answers_number: int):
        try:
            query = (f"UPDATE users "
                     f"SET correct_answers_number = COALESCE(%(correct_answers_number)s, correct_answers_number)"
                     f"WHERE id = %(user_id)s")
            data = {
                "user_id": user_id,
                "correct_answers_number": correct_answers_number
            }
            self.cursor.execute(query, data)
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при обновлении темы теста пользователя.", error)

    def get_user_correct_answers_number(self, user_id: int) -> int:
        try:
            query = f"SELECT correct_answers_number FROM users WHERE users.id = %(user_id)s"
            data = {"user_id": user_id}
            self.cursor.execute(query, data)
            res = self.cursor.fetchone()
            return res[0]
        except (Exception, Error) as error:
            print("Ошибка при получении темы теста пользователя.", error)

    def add_topic(self, title, description=None, user_id=None):
        try:
            query = f"INSERT INTO topics (title, description, user_id) VALUES (%(title)s, %(description)s, %(user_id)s)"
            data = {
                "title": title,
                "description": description,
                "user_id": user_id
            }
            self.cursor.execute(query, data)
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при добавлении темы.", error)

    def add_word(self, topic_id, word, word_translation, usage_example=None, usage_example_translation=None):
        try:
            query = (f"INSERT INTO words (topic_id, word, word_translation, usage_example, usage_example_translation) "
                     f"VALUES (%(topic_id)s, %(word)s, %(word_translation)s, %(usage_example)s, %(usage_example_translation)s)")
            data = {
                "topic_id": topic_id,
                "word": word,
                "word_translation": word_translation,
                "usage_example": usage_example,
                "usage_example_translation": usage_example_translation
            }
            self.cursor.execute(query, data)
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при добавлении слова.", error)

    def get_words_for_questions(self, user_id):
        try:
            query = (f"SELECT id, correct_answers_number, last_repeat "
                     f"FROM words LEFT JOIN (SELECT * FROM learning WHERE user_id = %(user_id)s) AS learning ON words.id = learning.word_id "
                     f"WHERE topic_id = (SELECT topic_id FROM users WHERE id = %(user_id)s) "
                     f"ORDER BY correct_answers_number")
            data = {"user_id": user_id}
            self.cursor.execute(query, data)
            res = self.cursor.fetchall()
            if res is None:
                return None
            return res
        except (Exception, Error) as error:
            print("Ошибка при получении вопроса для теста.", error)

    def get_fake_words_for_question(self, word_id) -> list[str, str, str]:
        try:
            query = (f"SELECT word_translation FROM words "
                     f"WHERE id != %(word_id)s "
                     f"ORDER BY RANDOM() LIMIT 3")
            data = {"word_id": word_id}
            self.cursor.execute(query, data)
            return [word[0] for word in self.cursor.fetchall()]
        except (Exception, Error) as error:
            print("Ошибка при получении вопроса для теста.", error)

    def add_word_in_test(self, user_id, word_id):
        try:
            query = f"INSERT INTO test (user_id, word_id) VALUES (%(user_id)s, %(word_id)s)"
            data = {
                "user_id": user_id,
                "word_id": word_id
            }
            self.cursor.execute(query, data)
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при добавлении слова в пул вопросов теста.", error)

    def get_word_from_test(self, user_id):
        try:
            query = (f"SELECT word_id, word, word_translation FROM test JOIN words ON test.word_id = words.id "
                     f"WHERE user_id = %(user_id)s AND is_right IS NULL "
                     f"ORDER BY RANDOM()")
            data = {"user_id": user_id}
            self.cursor.execute(query, data)
            res = self.cursor.fetchone()
            return res
        except (Exception, Error) as error:
            print("Ошибка при получении слова из пула вопросов теста.", error)

    def get_word_by_id_from_test(self, user_id, word_id):
        try:
            query = (f"SELECT word_id, word, word_translation FROM test JOIN words ON test.word_id = words.id "
                     f"WHERE user_id = %(user_id)s AND word_id = %(word_id)s AND is_right IS NULL")
            data = {
                "user_id": user_id,
                "word_id": word_id
            }
            self.cursor.execute(query, data)
            res = self.cursor.fetchone()
            return res
        except (Exception, Error) as error:
            print("Ошибка при получении слова из пула вопросов теста.", error)

    def set_is_right_in_test(self, user_id: int, word_id: int, is_right: bool):
        try:
            query = (f"UPDATE test "
                     f"SET is_right = COALESCE(%(is_right)s, is_right)"
                     f"WHERE user_id = %(user_id)s AND word_id = %(word_id)s")
            data = {
                "user_id": user_id,
                "word_id": word_id,
                "is_right": is_right
            }
            self.cursor.execute(query, data)
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при обновлении правильности вопроса.", error)

    def clear_test(self, user_id: int):
        try:
            query = (f"DELETE FROM test "
                     f"WHERE user_id = %(user_id)s")
            data = {"user_id": user_id}
            self.cursor.execute(query, data)
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при очистке пула вопросов теста пользователя.", error)

    def add_learning(self, user_id: int, word_id: int, correct_answers_number: int):
        try:
            query = (f"INSERT INTO learning (user_id, word_id, correct_answers_number, last_repeat)"
                     f"VALUES (%(user_id)s, %(word_id)s, %(correct_answers_number)s, %(last_repeat)s)")
            data = {
                "user_id": user_id,
                "word_id": word_id,
                "correct_answers_number": correct_answers_number,
                "last_repeat": datetime.datetime.now()
            }
            self.cursor.execute(query, data)
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при добавлении слова в таблицу прогресса обучения.", error)

    def update_learning(self, user_id: int, word_id: int, correct_answers_number: int):
        try:
            query = (f"UPDATE learning "
                     f"SET correct_answers_number = %(correct_answers_number)s, "
                     f"last_repeat = %(last_repeat)s "
                     f"WHERE user_id = %(user_id)s AND word_id = %(word_id)s")
            data = {
                "user_id": user_id,
                "word_id": word_id,
                "correct_answers_number": correct_answers_number,
                "last_repeat": datetime.datetime.now()
            }
            self.cursor.execute(query, data)
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при обновлении слова в таблице прогресса обучения.", error)

    def get_correct_answers_number_from_learning(self, user_id: int, word_id: int):
        try:
            query = (f"SELECT correct_answers_number FROM learning "
                     f"WHERE user_id = %(user_id)s AND word_id = %(word_id)s")
            data = {
                "user_id": user_id,
                "word_id": word_id
            }
            self.cursor.execute(query, data)
            res = self.cursor.fetchone()
            if res is None:
                return None
            return res[0]
        except (Exception, Error) as error:
            print("Ошибка при получении количества правильных ответов слова из таблицы прогресса обучения.", error)

    def get_is_right_grouped_words(self, user_id: int):
        try:
            query = (f"SELECT is_right, COUNT(*) FROM test "
                     f"WHERE user_id = %(user_id)s "
                     f"GROUP BY is_right ")
            data = {"user_id": user_id}
            self.cursor.execute(query, data)
            res = self.cursor.fetchall()
            return res
        except (Exception, Error) as error:
            print("Ошибка при получении количества ответов по правильности из таблицы прогресса обучения.", error)

    def get_word_usage_example_from_test(self, user_id):
        try:
            query = (f"SELECT usage_example, usage_example_translation FROM test JOIN words ON test.word_id = words.id "
                     f"WHERE user_id = %(user_id)s AND is_right IS NULL")
            data = {"user_id": user_id}
            self.cursor.execute(query, data)
            res = self.cursor.fetchone()
            return res
        except (Exception, Error) as error:
            print("Ошибка при получении слова из пула вопросов теста.", error)

    def get_learned_word_number(self, user_id: int) -> int | None:
        try:
            query = (f"SELECT COUNT(*) FROM learning "
                     f"WHERE correct_answers_number >= (SELECT correct_answers_number FROM users WHERE id = %(user_id)s)")
            data = {"user_id": user_id}
            self.cursor.execute(query, data)
            res = self.cursor.fetchone()
            if res is None:
                return None
            return res[0]
        except (Exception, Error) as error:
            print("Ошибка при получении количества выученных слов.", error)

    def get_word_number_in_topic(self, user_id: int) -> int | None:
        try:
            query = (f"SELECT COUNT(*) FROM words "
                     f"WHERE topic_id = (SELECT topic_id FROM users WHERE id = %(user_id)s)")
            data = {"user_id": user_id}
            self.cursor.execute(query, data)
            res = self.cursor.fetchone()
            if res is None:
                return None
            return res[0]
        except (Exception, Error) as error:
            print("Ошибка при получении количества слво в теме.", error)

    def get_user_last_repeat(self, user_id: int):
        try:
            query = f"SELECT last_repeat FROM users WHERE id = %(user_id)s"
            data = {"user_id": user_id}
            self.cursor.execute(query, data)
            res = self.cursor.fetchone()
            if res is None:
                return None
            return res[0]
        except (Exception, Error) as error:
            print("Ошибка при получении последнего прохождения теста пользователем.", error)

    def set_user_last_repeat(self, user_id: int):
        try:
            query = (f"UPDATE users "
                     f"SET last_repeat = COALESCE(%(last_repeat)s, last_repeat) "
                     f"WHERE id = %(user_id)s")
            data = {
                "user_id": user_id,
                "last_repeat": datetime.datetime.now()
            }
            self.cursor.execute(query, data)
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при обвновлении последнего прохождения теста пользователем.", error)

    def get_all_users_to_send_reminder(self, interval=30):
        try:
            query = f"SELECT id FROM users WHERE is_reminder_send = false AND last_repeat < NOW() - INTERVAL '%(interval)s minutes'"
            data = {"interval": interval}
            self.cursor.execute(query, data)
            res = self.cursor.fetchall()
            if res is None:
                return None
            return res
        except (Exception, Error) as error:
            print("Ошибка при получении пользователей для отправки напоминаний.", error)

    def set_is_reminder_send(self, user_id: int, is_reminder_send: bool):
        try:
            query = (f"UPDATE users "
                     f"SET is_reminder_send = %(is_reminder_send)s "
                     f"WHERE id = %(user_id)s")
            data = {
                "user_id": user_id,
                "is_reminder_send": is_reminder_send
            }
            self.cursor.execute(query, data)
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при обновлении флага отправки напоминания.", error)
