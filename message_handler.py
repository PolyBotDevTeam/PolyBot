# Deprecated module

import functools
import time

import vk_api
import pymysql

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
