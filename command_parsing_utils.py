import db_utils as _db_utils
import vk_utils as _vk_utils


def try_to_identify_id(text, cur, *, vk=vk):
    if _vk_utils.is_mention(text):
        result = _vk_utils.id_by_mention(text)
    else:
        result = _player_id_by_name(text, cur, vk=vk)
    return result


def _player_id_by_name(name, cur, *, vk):
    try:
        return _id_by_nickname(name, cur)
    except ValueError:
        pass
    try:
        return _player_id_by_username(name, cur, vk=vk)
    except ValueError:
        pass
    raise ValueError


def _id_by_nickname(nickname, cur):
    if not _db_utils.exists(cur, 'players', 'nickname = %s', nickname):
        raise ValueError
    cur.execute('SELECT player_id FROM players WHERE nickname = %s', nickname)
    user_id, *duplicates = cur.fetchall()
    if duplicates:
        raise RuntimeError('nicknames conflict: %s' % nickname)
    (user_id,) = user_id
    return user_id


def _player_id_by_username(username, cur, *, vk):
    uname_need = username
    del username
    uname_need = uname_need.lower()

    players_ids = _db_utils.execute(cur, 'SELECT player_id FROM players;')
    players_ids = [uid for (uid,) in players_ids]

    usernames = _vk_utils.fetch_usernames(players_ids, vk=vk)
    usernames = [uname.lower() for uname in usernames]

    if uname_need not in usernames and uname_need.count(' ') == 1:
        last_name, first_name = uname_need.split(' ')
        uname_need = first_name + ' ' + last_name
    if uname_need not in usernames:
        raise ValueError(uname_need)

    return players_ids[usernames.index(uname_need)]
