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
    new_string, *parts = string.split('[')
    for s in parts:
        new_string += '['
        if s.startswith('id'):
            i = 0
            while i < len(s) and s[i] != '|':
                i += 1
            if i == len(s):
                new_string += s[:i]
            else:
                new_string += address_replacement
            new_string += s[i:]
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


def create_mention(user_id, vk):
    prefix = 'id' if user_id >= 0 else 'club'
    name = fetch_username(user_id, vk=vk)
    return f'[{prefix}{user_id}|{name}]'


def fetch_usernames(users_ids, vk):
    users_ids = tuple(users_ids)
    assert len(users_ids) <= 1000

    ids_to_fetch = tuple(filter(lambda uid: uid > 0, users_ids))
    response = vk.users.get(user_ids=ids_to_fetch) if ids_to_fetch else []

    users_by_ids = _collections.defaultdict(lambda: {'first_name': 'NULL', 'last_name': 'NULL'})
    for user in response:
        users_by_ids[user['id']] = user

    result = []
    for user_id in users_ids:
        if user_id >= 0:
            username = '{first_name} {last_name}'.format(**users_by_ids[user_id])
        else:
            username = vk.groups.getById(group_id=-user_id)[0]['name']
        result.append(username)
    return result


def fetch_username(user_id, vk):
    [username] = fetch_usernames([user_id], vk=vk)
    return username


def fetch_chat_members_ids(chat_id, vk):
    peer_id = peer_id_by_chat_id(chat_id)
    members = vk.messages.getConversationMembers(peer_id=peer_id)['items']
    members_ids = [member['member_id'] for member in members]
    return members_ids
