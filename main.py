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


polybot_welcome = """Приветствую, {username}!

Чтобы зарегистрироваться в боте, отправьте сообщение [club{group_id}|/регистрация Nickname], указав вместо Nickname свой ник в Политопии."""


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


def _process_event(event, *, vk, polybot_database):
    # print('New Event:', event, end='\n\n', flush=True)
    if event.type != VkBotEventType.MESSAGE_NEW:
        return
    message = event.obj.message

    tournament_chat_peer_id = vk_utils.peer_id_by_chat_id(settings.tournament_chat_id)
    if message['peer_id'] == tournament_chat_peer_id:
        action = message.get('action')
        if action is not None and action['type'] == 'chat_invite_user_by_link':
            username = vk_utils.fetch_username(message['from_id'], vk=vk).split()[0]
            text = 'Привет, {username}!\nПрочитай правила в закреплённом сообщении.'.format(username=username)
            vk.messages.send(message=text, peer_id=tournament_chat_peer_id, random_id=vk_api.utils.get_random_id())

    if message['peer_id'] == vk_utils.peer_id_by_chat_id(settings.main_chat_id):
        action = message.get('action')
        if action is not None and action['type'] == 'chat_invite_user_by_link':
            username = vk_utils.fetch_username(message['from_id'], vk=vk).split()[0]
            text = polybot_welcome.format(username=username, group_id=group_id)
            vk.messages.send(message=text, peer_id=message['peer_id'], random_id=vk_api.utils.get_random_id())

    text = message['text']
    if not text:
        return
    prefix = text[0]
    if prefix in ('/', '!'):
        if event.from_chat:
            print(text, end='\n\n', file=settings.commands_log_file, flush=True)
            print(text, end='\n\n', file=settings.errors_log_file, flush=True)
            chat_id = vk_utils.chat_id_by_peer_id(message['peer_id'])
            if message['text'] == '!restart' and message['from_id'] in settings.admins_ids and chat_id in settings.admin_chats:
                sys.exit()
            message_handler.process_message_chat(
                vk=vk,
                u=message['from_id'],
                chat=chat_id,
                command=text,
                prefix=prefix,
                user_message=message,
                database=polybot_database
            )
        elif event.from_user:
            pass


if __name__ == '__main__':
    main()
