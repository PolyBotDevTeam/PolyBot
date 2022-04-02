import itertools

import utils
import vk_utils
import vk_actions

import command_system
import elo as elo_module

import settings


def _is_int(x):
    try:
        int(x)
        result = True
    except ValueError:
        result = False
    return result


def top(max_places_count, *, category, cursor, vk):
    title_template = 'ТОП-{places_count}'

    elo_module.recalculate(cur=cursor)

    if category in ('', 'сумма', 'sum'):
        cursor.execute('SELECT player_id, host_elo, elo FROM players ORDER BY (host_elo + elo) DESC;')
        top_item_template = '{place}. {host_emoji}{away_emoji} {player_name}\n' \
                            '{indent}{host_elo} / {away_elo} ЭЛО\n'
    elif category in ('хост', 'host', 'первый', 'first'):
        title_template += ' (хост)'
        cursor.execute('SELECT player_id, host_elo, elo FROM players ORDER BY host_elo DESC;')
        top_item_template = '{place}. {host_emoji} {player_name}\n' \
                            '{indent}{host_elo} ЭЛО\n'
    elif category in ('второй', 'away', 'second'):
        title_template += ' (второй)'
        cursor.execute('SELECT player_id, host_elo, elo FROM players ORDER BY elo DESC;')
        top_item_template = '{place}. {away_emoji} {player_name}\n' \
                            '{indent}{away_elo} ЭЛО\n'
    else:
        message_text = 'Неправильный формат ввода. Попробуйте просто /топ.'
        return [message_text]

    members_ids = vk_utils.fetch_chat_members_ids(settings.main_chat_id, vk=vk)

    top_players_data = (
        (player_id, host_elo, away_elo)
        for player_id, host_elo, away_elo in cursor
        if player_id in members_ids
    )

    top_players_data = itertools.islice(top_players_data, max_places_count)
    top_players_data = tuple(top_players_data)
    places_count = len(top_players_data)

    title = title_template.format(places_count=places_count)

    message_text = f'{title}:\n'

    for place, (player_id, host_elo, away_elo) in enumerate(top_players_data, 1):
        digits_n = len(str(places_count))
        numeric_space = '\u2007'
        place = str(place).rjust(digits_n, numeric_space)

        if digits_n < 2:
            indent = numeric_space * digits_n + numeric_space
        else:
            indent = numeric_space * (digits_n - 2) + (numeric_space + ' ') * 2

        host_emoji, away_emoji = elo_module.emoji_by_elo(host_elo, away_elo)

        cursor.execute('SELECT nickname FROM players WHERE player_id = %s;', player_id)
        [[nickname]] = cursor
        nickname = utils.truncate_string(nickname, max_length=15, truncated_end='..')

        player_name = vk_utils.create_mention(player_id, mention_text=nickname)

        top_item = top_item_template.format(
            place=place,
            player_name=player_name,
            host_elo=host_elo,
            away_elo=away_elo,
            host_emoji=host_emoji,
            away_emoji=away_emoji,
            indent=indent
        )

        message_text += top_item

    message = vk_actions.Message(text=message_text, disable_mentions=True)

    return [message]


def _process_top_command(player_id, command_text, *, cursor, vk, **kwargs):
    args = command_text.split()

    places_count_need = None
    for arg in tuple(args):
        if _is_int(arg):
            places_count_need = int(arg)
            args.remove(arg)
            break
    if places_count_need is None:
        places_count_need = 10

    if places_count_need < 0:
        places_count_need = 0

    max_places_count = 20
    if places_count_need > max_places_count:
        places_count_need = max_places_count

    [category] = args if args else ['sum']

    result = top(places_count_need, category=category, cursor=cursor, vk=vk)

    return result


top_command = command_system.Command(
    process=_process_top_command,
    keys=['топ', 'top'],
    description='Игроки с наивысшим ЭЛО-рейтингом',
    signature='(_ / хост / второй)',
    allow_users=True
)
