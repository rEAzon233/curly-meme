import os
import sqlite3
import vk_api
from datetime import date
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType


def do_auth_sqlite():  # Authorization in database
    conn = sqlite3.connect('users_data.sql')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
    id int auto_increment primary key, user_id int, 
    registration_time text)''')
    conn.commit()
    cur.close()
    conn.close()


def checking_user_id(received_id):  # Checking user in database
    conn = sqlite3.connect('users_data.sql')
    cur = conn.cursor()
    in_exist = True

    cur.execute(f'SELECT user_id FROM users')
    checking = cur.fetchall()

    for el in checking:
        if received_id == el[0]:
            in_exist = False

    cur.close()
    conn.close()

    return in_exist


def added_user(user_id):  # Added user in database
    conn = sqlite3.connect('users_data.sql')
    cur = conn.cursor()

    cur.execute(f"INSERT INTO users (user_id, registration_time) VALUES (?, ?)", (user_id, date.today()))
    conn.commit()
    cur.close()
    conn.close()


def callback():  # Displaying a list of users
    conn = sqlite3.connect('users_data.sql')
    cur = conn.cursor()

    cur.execute('SELECT user_id, registration_time FROM users')
    users = cur.fetchall()
    info = f'Общее количество участников: {len(users)}\n'

    for el in users:
        info += f'Id: {el[0]}, дата: {el[1]}\n'
    cur.close()
    conn.close()

    return info


def do_auth_vk():  # Authorization in VK
    load_dotenv()
    main_token = os.getenv('ACCESS_TOKEN')
    vk_session = vk_api.VkApi(token=main_token)

    return vk_session


def send_message(new_id, text):    # Response message
    do_auth_vk().method('messages.send', {'user_id': new_id, 'message': text, 'random_id': 0})


def message_check():    # Checking a message for an audio message
    longpoll = VkLongPoll(do_auth_vk())

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            user_id = event.user_id

            if event.to_me and 'attach1_kind' in event.attachments:
                do_auth_sqlite()

                if checking_user_id(user_id) and event.attachments['attach1_kind'] == 'audiomsg':
                    added_user(user_id)
                    send_message(user_id, 'Спасибо, сообщение получено!')
                else:
                    send_message(user_id, 'Ваше сообщение уже было получено.')
            elif event.to_me and event.text.lower() == 'полный список участников':
                try:
                    send_message(user_id, callback())
                except Exception as error:
                    print(error)
                    send_message(user_id, 'Ошибка')


message_check()
