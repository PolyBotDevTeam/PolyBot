import collections as _collections


CHAT_PEER_ID_PREFIX = 2 * 10**9


def peer_id_by_chat_id(chat_id):
    return CHAT_PEER_ID_PREFIX + chat_id


def chat_id_by_peer_id(peer_id):
    return peer_id - CHAT_PEER_ID_PREFIX


def protect_empty_lines(text):
    return text.replace('\n\n', '\n \n')


def highlight_marked_text_areas(
    message_text, *,
    start_syntax='<',
    stop_syntax='>',
    mentions_address_str='club0'
):
    message_text = message_text.replace(start_syntax, f'[{mentions_address_str}|')
    message_text = message_text.replace(stop_syntax, ']')
    return message_text


def break_mentions(string, *, address_replacement='club0'):
    new_string, *parts_to_process = string.split('[')
    for part in parts_to_process:
        new_string += '['
        if part.startswith('id') and '|' in part:
            old_address, remainder = part.split('|', 1)
            if ']' in remainder:
                part = address_replacement + '|' + remainder
        new_string += part

    new_string = new_string.replace('all', 'аll').replace('everyone', 'еveryone').replace('online', 'оnline').replace('here', 'hеre')
    new_string = new_string.replace('все', 'вcе').replace('онлайн', 'oнлайн').replace('тут', 'тyт').replace('здесь', 'здeсь')
    return new_string


class InvalidMentionError(ValueError):
    pass


def is_mention(mention):
    try:
        id_by_mention(mention)
    except InvalidMentionError:
        return False
    return True


def id_by_mention(mention):
    if not (mention.startswith('[') and mention.endswith(']') and '|' in mention):
        raise InvalidMentionError
    core = mention.split('|')[0][1:]

    prefix = 'id'
    if not core.startswith(prefix):
        prefix = 'club'
    if not core.startswith(prefix):
        raise InvalidMentionError

    body = core[len(prefix):]
    try:
        value = int(body)
    except ValueError:
        raise InvalidMentionError

    return +value if prefix == 'id' else -value


def create_mention(user_id, mention_text=None, *, vk=None):
    prefix = 'id' if user_id >= 0 else 'club'
    user_address = f'{prefix}{abs(user_id)}'

    if mention_text is None:
        mention_text = fetch_username(user_id, vk=vk)

    return f'[{user_address}|{mention_text}]'


def fetch_usernames(users_ids, vk, *, lang=None):
    if lang is None:
        lang = 'ru'

    users_ids = tuple(users_ids)
    assert len(users_ids) <= 1000

    ids_to_fetch = tuple(filter(lambda uid: uid > 0, users_ids))
    response = vk.users.get(user_ids=ids_to_fetch, lang=lang) if ids_to_fetch else []

    users_by_ids = _collections.defaultdict(lambda: {'first_name': 'NULL', 'last_name': 'NULL'})
    for user in response:
        users_by_ids[user['id']] = user

    result = []
    for user_id in users_ids:
        if user_id >= 0:
            username = '{first_name} {last_name}'.format(**users_by_ids[user_id])
        else:
            username = vk.groups.getById(group_id=-user_id, lang=lang)[0]['name']
        result.append(username)
    return result


def fetch_username(user_id, vk, *, lang=None):
    [username] = fetch_usernames([user_id], vk=vk, lang=lang)
    return username


def fetch_chat_members_ids(chat_id, vk):
    peer_id = peer_id_by_chat_id(chat_id)
    members = vk.messages.getConversationMembers(peer_id=peer_id)['items']
    members_ids = [member['member_id'] for member in members]
    return members_ids
