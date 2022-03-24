import functools
import importlib
import os
import sys
import time

import vk_api
import pymysql

import command_system
import utils
import db_utils
import vk_utils
import vk_actions
import settings


# Deprecated
# TODO: Remove
_session = vk_api.VkApi(token=settings.token)
api = _session.get_api()


# TODO: deprecated
def create_connection():
    connection = pymysql.connect(
        host=settings.host,
        user=settings.user,
        password=settings.password,
        database=settings.database,
        autocommit=True
    )
    return connection


def process_message_from_chat(message, *, vk, database):
    chat_id = vk_utils.chat_id_by_peer_id(message['peer_id'])

    triggering_prefixes = {'/', '!'}
    text = message['text']

    if not any(text.startswith(prefix) for prefix in triggering_prefixes):
        return

    assert text
    prefix = text[0]
    user_command = text

    message_time = message['date']
    actor = message['from_id']

    for file in [settings.commands_log_file, settings.errors_log_file]:
        print(message_time, actor, repr(text), sep='\n', end='\n\n', file=file, flush=True)

    if user_command == '!restart' and actor in settings.admins_ids and chat_id in settings.admin_chats:
        sys.exit()

    def _are_commands_equal(command_str_1, command_str_2):
        prefix_1, name_1, command_text_1 = command_system.parse_command(command_str_1)
        prefix_2, name_2, command_text_2 = command_system.parse_command(command_str_2)
        try:
            names_1 = command_system.get_command(prefix_1+name_1).keys
        except command_system.CommandNotFoundError:
            names_1 = []
        return prefix_1 == prefix_2 and name_2 in names_1

    # TODO: command attr "admin_chat_required"
    if chat_id not in settings.admin_chats:
        whitelisted_commands = ['/спать', '/выбор_племени', '!py']
        is_command_whitelisted = any(_are_commands_equal(user_command, x) for x in whitelisted_commands)
        if not is_command_whitelisted:
            return

    actions = command_system.process_command(
        actor,
        user_command,
        message,
        process_exception=functools.partial(process_exception, vk=vk),
        database=database,
        vk=vk
    )

    execute_actions(actions, vk=vk, chat_id=chat_id)


def execute_actions(actions, *, vk, chat_id):
    for action in actions:
        if isinstance(action, vk_actions.Message):
            send_message(message=action, vk=vk, chat_id=chat_id)
        else:
            raise TypeError('unknown action type:', type(action))


def process_exception(exception, *, vk, is_important=True):
    utils.print_exception(exception, file=settings.errors_log_file)
    error_message = utils.represent_exception(exception)
    # TODO: Make it guaranteed (now it can just raise ApiError and forget to notify latter)
    if is_important:
        send_message(error_message, vk=vk, chat_id=settings.polydev_chat_id)


def send_message(message, vk, **kwargs):
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


def try_to_identify_id(text, cur):
    if vk_utils.is_mention(text):
        result = vk_utils.id_by_mention(text)
    else:
        result = player_id_by_name(text, cur)
    return result


def player_id_by_name(name, cur):
    try:
        return id_by_nickname(name, cur)
    except ValueError:
        pass
    try:
        return player_id_by_username(name, cur)
    except ValueError:
        pass
    raise ValueError


def id_by_nickname(nickname, cur):
    if not db_utils.exists(cur, 'players', 'nickname = %s', nickname):
        raise ValueError
    cur.execute('SELECT player_id FROM players WHERE nickname = %s', nickname)
    user_id, *duplicates = cur.fetchall()
    if duplicates:
        raise RuntimeError('nicknames conflict: %s' % nickname)
    (user_id,) = user_id
    return user_id


def player_id_by_username(username, cur):
    uname_need = username
    del username
    uname_need = uname_need.lower()

    players_ids = db_utils.select(cur, 'SELECT player_id FROM players;')
    players_ids = [uid for (uid,) in players_ids]

    usernames = fetch_usernames(players_ids)
    usernames = [uname.lower() for uname in usernames]

    if uname_need not in usernames and uname_need.count(' ') == 1:
        last_name, first_name = uname_need.split(' ')
        uname_need = first_name + ' ' + last_name
    if uname_need not in usernames:
        raise ValueError(uname_need)

    return players_ids[usernames.index(uname_need)]


fetch_usernames = functools.partial(vk_utils.fetch_usernames, vk=api)
username = functools.partial(vk_utils.fetch_username, vk=api)
create_mention = functools.partial(vk_utils.create_mention, vk=api)
