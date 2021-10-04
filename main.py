import io
import sys

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from polybot_database import PolyBotDatabase
import settings
from settings import group_id
import command_system
import message_handler
import utils
import vk_utils


def main():
    print('PolyBot Started!', flush=True)

    vk_session = vk_api.VkApi(token=settings.token)
    vk = vk_session.get_api()

    longpoll = VkBotLongPoll(vk_session, group_id)

    try:
        message_handler.load_modules()
    except ImportError as e:
        [exceptions] = e.args
        errors_log = io.StringIO()
        for error in exceptions:
            utils.print_exception(error, file=errors_log)
        message_handler.send_message(errors_log.getvalue(), vk=vk, chat_id=settings.polydev_chat_id)

    polybot_database = PolyBotDatabase(create_connection=message_handler.create_connection)

    while True:
        try:
            for event in longpoll.listen():
                _process_event(event, vk=vk, polybot_database=polybot_database)
        except Exception as e:
            message_handler.process_exception(e, vk=vk)
            sys.exit()


polybot_welcome = """Приветствую, {username}!

Чтобы зарегистрироваться в боте, отправьте сообщение [club{group_id}|/регистрация Nickname], указав вместо Nickname свой ник в Политопии."""


def _process_event(event, *, vk, polybot_database):
    # print('New Event:', event, end='\n\n', flush=True)
    if event.type != VkBotEventType.MESSAGE_NEW or not event.from_chat:
        return

    message = event.obj.message
    chat_id = vk_utils.chat_id_by_peer_id(message['peer_id'])

    if chat_id in {settings.main_chat_id, settings.tournament_chat_id}:
        if chat_id == settings.main_chat_id:
            template = polybot_welcome
        else:
            assert chat_id == settings.tournament_chat_id
            template = 'Привет, {username}!\nПрочитай правила в закреплённом сообщении.'

        action = message.get('action')
        if action is not None and action['type'] == 'chat_invite_user_by_link':
            username = vk_utils.fetch_username(message['from_id'], vk=vk).split()[0]
            text = template.format(username=username, group_id=group_id)
            message_handler.send_message(text, vk=vk, chat_id=chat_id)

    message_handler.process_message_from_chat(
        vk=vk,
        message=message,
        database=polybot_database
    )


if __name__ == '__main__':
    main()
