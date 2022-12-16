import enum
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


class _SortingMode(enum.Enum):
    SUM = 1
    HOST = 2
    AWAY = 3


def top(max_places_count, *, sorting_mode, cursor, vk):
    title_template = 'ТОП-{places_count}'

    elo_module.recalculate(cur=cursor)

    if sorting_mode == _SortingMode.SUM:
        cursor.execute('SELECT player_id, host_elo, away_elo FROM players ORDER BY (host_elo + away_elo) DESC;')
        top_item_template = '{place}. {host_emoji}{away_emoji} {player_name}\n' \
                            '{indent}{host_elo} / {away_elo} ЭЛО\n'
    elif sorting_mode == _SortingMode.HOST:
        title_template += ' (хост)'
        cursor.execute('SELECT player_id, host_elo, away_elo FROM players ORDER BY host_elo DESC;')
        top_item_template = '{place}. {host_emoji} {player_name}\n' \
                            '{indent}{host_elo} ЭЛО\n'
    elif sorting_mode == _SortingMode.AWAY:
        title_template += ' (второй)'
        cursor.execute('SELECT player_id, host_elo, away_elo FROM players ORDER BY away_elo DESC;')
        top_item_template = '{place}. {away_emoji} {player_name}\n' \
                            '{indent}{away_elo} ЭЛО\n'
    else:
        message_text = 'Данный критерий сортировки пока не поддерживается.'
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

    if not args:
        sorting_mode = _SortingMode.SUM
    elif len(args) == 1:
        [mode_name] = args
        mode_name = mode_name.lower()
        if mode_name in {'сумма', 'sum'}:
            sorting_mode = _SortingMode.SUM
        elif mode_name in {'хост', 'host', 'первый', 'first'}:
            sorting_mode = _SortingMode.HOST
        elif mode_name in {'второй', 'away', 'second'}:
            sorting_mode = _SortingMode.AWAY
        else:
            return [f'Неизвестный тэг: "{mode_name}". Узнать о допустимых значениях можно через /помощь топ']
    else:
        return ['Слишком много аргументов. Узнать о параметрах команды можно через /помощь топ']

    result = top(places_count_need, sorting_mode=sorting_mode, cursor=cursor, vk=vk)

    return result


top_command = command_system.Command(
    process=_process_top_command,
    keys=['топ', 'top'],
    description='Игроки с наивысшим ЭЛО-рейтингом',
    signature='(_ / хост / второй)',
    allow_users=True
)
