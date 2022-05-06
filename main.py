import io
import os
import time
import sys

import requests.exceptions
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll

from polybot import PolyBot
from polybot_database import PolyBotDatabase
import settings
import command_system
import message_handler
import utils


def main():
    print('PolyBot Started!', flush=True)

    vk_session = vk_api.VkApi(token=settings.token)
    vk = vk_session.get_api()

    message_handler.send_message('PolyBot Started!', vk=vk, chat_id=settings.polydev_chat_id)

    longpoll = VkBotLongPoll(vk_session, settings.group_id)

    try:
        commands_path = os.path.join(settings.project_folder, 'commands')
        command_system.load_commands_from_directory(commands_path)
    except ImportError as e:
        [exceptions] = e.args
        errors_log = io.StringIO()
        for error in exceptions:
            utils.print_exception(error, file=errors_log)
        message_handler.send_message(errors_log.getvalue(), vk=vk, chat_id=settings.polydev_chat_id)

    polybot_database = PolyBotDatabase(create_connection=message_handler.create_connection)

    polybot = PolyBot(
        vk=vk,
        database=polybot_database,
        settings=settings,
        message_handler=message_handler,
        command_system=command_system
    )

    try:
        while True:
            try:
                new_events = longpoll.check()
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                new_events = []
                _process_exception_from_longpoll_check(e, vk=vk)

            for event in new_events:
                polybot.process_vk_event(event)

            polybot.process_new_time(time.time())

    except Exception as e:
        message_handler.process_exception(e, vk=vk)
        sys.exit()


def _process_exception_from_longpoll_check(exception, *, vk):
    notification_text = f'"longpoll.check()" failed: {repr(exception)}'
    message_handler.send_message(notification_text, vk=vk, chat_id=settings.polydev_chat_id)
    message_handler.process_exception(exception, vk=vk, is_important=False)


if __name__ == '__main__':
    main()
