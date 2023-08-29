import os
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv


def do_auth():  # Авторизация
    load_dotenv()

    main_token = os.getenv('ACCESS_TOKEN')
    vk_session = vk_api.VkApi(token=main_token)
    return vk_session


def send_message(new_id, text):    # Ответное сообщение
    do_auth().method('messages.send', {'user_id': new_id, 'message': text, 'random_id': 0})


def message_check():    # Проверка сообщения на наличие ГС
    longpoll = VkLongPoll(do_auth())

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me and 'attach1_kind' in event.attachments:
                user_id = event.user_id

                if event.attachments['attach1_kind'] == 'audiomsg':
                    send_message(user_id, 'Спасибо, сообщение получено!')


message_check()
