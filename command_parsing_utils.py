import db_utils as _db_utils
import vk_utils as _vk_utils


def try_to_identify_id(text, cur, *, vk):
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


def _player_id_by_username(username, cursor, *, vk):
    target_username = username
    del username

    players_ids = _db_utils.execute(cursor, 'SELECT player_id FROM players ORDER BY host_elo + away_elo DESC;')
    players_ids = [uid for (uid,) in players_ids]

    players_usernames = _vk_utils.fetch_usernames(players_ids, vk=vk)

    best_candidate = _which_username_fits_best(players_usernames, target_username=target_username)

    return players_ids[players_usernames.index(best_candidate)]


def _which_username_fits_best(username_candidates, *, target_username):
    for candidate in username_candidates:
        if _does_username_fit(candidate=candidate, target=target_username):
            return candidate

    raise ValueError(target_username)


def _does_username_fit(*, candidate, target):
    alternative_target = ' '.join(target.split()[::-1])
    return _normalize_username(target) in _normalize_username(candidate) \
        or _normalize_username(alternative_target) in _normalize_username(candidate)


def _normalize_username(username):
    return ' '.join(username.lower().split())
