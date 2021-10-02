import sys

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from polybot_database import PolyBotDatabase
import settings
from settings import token, group_id, errors_log_file, commands_log_file, admin_chats, admins_ids
import command_system
import message_handler
from message_handler import process_message_chat, load_modules, username as fetch_username
from utils import print_exception
import vk_utils


polybot_welcome = """Приветствую, {username}!

Чтобы зарегистрироваться в боте, отправьте сообщение [club{group_id}|/регистрация Nickname], указав вместо Nickname свой ник в Политопии."""


def main():
    print('PolyBot Started!', flush=True)
    load_modules()

    polybot_database = PolyBotDatabase(create_connection=message_handler.create_connection)

    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()

    longpoll = VkBotLongPoll(vk_session, group_id)

    while True:
        try:
            for event in longpoll.listen():
                # print('New Event:', event, end='\n\n', flush=True)
                if event.type != VkBotEventType.MESSAGE_NEW:
                    continue
                message = event.obj.message

                # TODO: Move out this code

                tournament_chat_peer_id = vk_utils.peer_id_by_chat_id(settings.tournament_chat_id)
                if message['peer_id'] == tournament_chat_peer_id:
                    action = message.get('action')
                    if action is not None and action['type'] == 'chat_invite_user_by_link':
                        username = fetch_username(message['from_id']).split()[0]
                        text = 'Привет, {username}!\nПрочитай правила в закреплённом сообщении.'.format(username=username)
                        vk.messages.send(message=text, peer_id=tournament_chat_peer_id, random_id=vk_api.utils.get_random_id())

                if message['peer_id'] == vk_utils.peer_id_by_chat_id(settings.main_chat_id):
                    action = message.get('action')
                    if action is not None and action['type'] == 'chat_invite_user_by_link':
                        username = fetch_username(message['from_id']).split()[0]
                        text = polybot_welcome.format(username=username, group_id=group_id)
                        vk.messages.send(message=text, peer_id=message['peer_id'], random_id=vk_api.utils.get_random_id())

                text = message['text']
                if not text:
                    continue
                prefix = text[0]
                if prefix in ('/', '!'):
                    if event.from_chat:
                        print(text, end='\n\n', file=commands_log_file, flush=True)
                        print(text, end='\n\n', file=errors_log_file, flush=True)
                        chat_id = vk_utils.chat_id_by_peer_id(message['peer_id'])
                        if message['text'] == '!restart' and message['from_id'] in admins_ids and chat_id in admin_chats:
                            sys.exit()
                        process_message_chat(
                            token=token,
                            u=message['from_id'],
                            chat=chat_id,
                            command=text,
                            prefix=prefix,
                            user_message=message,
                            database=polybot_database
                        )
                    elif event.from_user:
                        pass

        except Exception as e:
            print_exception(e, file=errors_log_file)
            sys.exit()


if __name__ == '__main__':
    main()
