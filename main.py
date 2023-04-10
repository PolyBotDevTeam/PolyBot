import io
import os
import time
import sys as _sys

import pymysql as _pymysql
import requests.exceptions
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll

from polybot import PolyBot
from polybot_database import PolyBotDatabase
import vk_actions

import settings
import command_system
import utils


def main():
    _log_polybot_script_start()

    vk_session = vk_api.VkApi(token=settings.token)
    vk = vk_session.get_api()

    longpoll = VkBotLongPoll(vk_session, settings.group_id)

    try:
        commands_path = os.path.join(settings.project_folder, 'commands')
        command_system.load_commands_from_directory(commands_path)
    except ImportError as e:
        [exceptions] = e.args
        errors_log = io.StringIO()
        for error in exceptions:
            utils.print_exception(error, file=errors_log)
        _send_message(errors_log.getvalue(), vk=vk, chat_id=settings.polydev_chat_id)

    polybot_database = PolyBotDatabase(
        create_connection=lambda: _create_connection(settings)
    )

    polybot = PolyBot(
        vk=vk,
        database=polybot_database,
        settings=settings,
        send_message=_send_message,
        process_exception=_process_exception,
        restart=_restart,
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
        _process_exception(e, vk=vk)
        _restart()


def _log_polybot_script_start():
    print('PolyBot/main.py started at', time.time(), flush=True)


def _process_exception_from_longpoll_check(exception, *, vk):
    notification_text = f'"longpoll.check()" failed: {repr(exception)}'
    _send_message(notification_text, vk=vk, chat_id=settings.polydev_chat_id)
    _process_exception(exception, vk=vk, is_important=False)


def _process_exception(exception, *, vk, is_important=True):
    utils.print_exception(exception, file=settings.errors_log_file)
    error_message = utils.represent_exception(exception)
    # TODO: Make it guaranteed (now it can just raise ApiError and forget to notify latter)
    if is_important:
        _send_message(error_message, vk=vk, chat_id=settings.polydev_chat_id)


def _send_message(message, vk, **kwargs):
    if not isinstance(message, vk_actions.Action) and isinstance(message, str):
        message = vk_actions.Message(text=str(message))
    while True:
        try:
            vk.messages.send(
                random_id=vk_api.utils.get_random_id(),
                message=message.text, attachment=message.attachments, disable_mentions=message.disable_mentions,
                **kwargs
            )
            break
        except vk_api.exceptions.ApiError as e:
            if e.code == 9:
                time.sleep(20)
            else:
                raise


def _create_connection(settings):
    connection = _pymysql.connect(
        host=settings.host,
        user=settings.user,
        password=settings.password,
        database=settings.database,
        autocommit=True
    )
    return connection


def _restart():
    _sys.exit()


if __name__ == '__main__':
    main()
