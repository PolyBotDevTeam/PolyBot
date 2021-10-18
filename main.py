import io
import sys

import requests.exceptions
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from polybot_database import PolyBotDatabase
import settings
import command_system
import message_handler
import utils
import vk_utils


def main():
    print('PolyBot Started!', flush=True)

    vk_session = vk_api.VkApi(token=settings.token)
    vk = vk_session.get_api()

    longpoll = VkBotLongPoll(vk_session, settings.group_id)

    try:
        message_handler.load_commands()
    except ImportError as e:
        [exceptions] = e.args
        errors_log = io.StringIO()
        for error in exceptions:
            utils.print_exception(error, file=errors_log)
        message_handler.send_message(errors_log.getvalue(), vk=vk, chat_id=settings.polydev_chat_id)

    polybot_database = PolyBotDatabase(create_connection=message_handler.create_connection)

    try:
        while True:
            try:
                new_events = longpoll.check()
            except requests.exceptions.ReadTimeout as e:
                new_events = []
                _process_read_timeout_exception(e, vk=vk)

            for event in new_events:
                _process_event(event, vk=vk, polybot_database=polybot_database)

    except Exception as e:
        message_handler.process_exception(e, vk=vk)
        sys.exit()


def _process_read_timeout_exception(exception, *, vk):
    message_handler.send_message('Yet Another ReadTimeout', vk=vk, chat_id=settings.polydev_chat_id)
    message_handler.process_exception(exception, vk=vk, is_important=False)


polybot_welcome = """Приветствую, {username}!

Чтобы зарегистрироваться в боте, отправьте сообщение </регистрация Nickname>, указав вместо Nickname свой ник в Политопии."""

polybot_welcome = vk_utils.highlight_marked_text_areas(polybot_welcome)


elo_help = '''ЭЛО - это система рейтингов.

Основная идея в том, что на основе рейтингов двух игроков мы можем найти ожидаемый шанс победы каждого из них.
Например, разница в 400 рейтинга подразумевает разницу в шансах в 10 раз.

Когда один игрок побеждает другого, их рейтинги слегка корректируются в зависимости от того, насколько результат соответствует ожиданиям.

Несколько примеров того, как меняется рейтинг победителя:
* Шанс победы 100% --> рейтинг победителя не меняется
* Шанс победы 80% --> +10 рейтинга
* Шанс победы 60% --> +20 рейтинга
* Шанс победы 40% --> +30 рейтинга
* Шанс победы 20% --> +40 рейтинга
* Шанс победы 0% --> +50 рейтинга

Проигравший теряет столько же рейтинга, сколько получает победивший.

Таким образом, рейтинг будет постепенно корректироваться в зависимости от того, какие результаты демонстрирует игрок.'''


def _process_event(event, *, vk, polybot_database):
    if event.type != VkBotEventType.MESSAGE_NEW:
        return

    message = event.obj.message
    if message['text'].lower().replace('"', '').replace('?', '') == 'что такое эло':
        message_handler.send_message(elo_help, vk=vk, peer_id=message['peer_id'])

    if not event.from_chat:
        return

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
            text = template.format(username=username)
            message_handler.send_message(text, vk=vk, chat_id=chat_id)

    message_handler.process_message_from_chat(
        vk=vk,
        message=message,
        database=polybot_database
    )


if __name__ == '__main__':
    main()
