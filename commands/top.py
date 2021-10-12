import command_system
import elo as elo_module
import itertools
import settings
import vk_utils


def _is_int(x):
    try:
        int(x)
        result = True
    except ValueError:
        result = False
    return result


def top(max_count, *, category, cursor, vk):
    title_format = 'ТОП-{count}'

    elo_module.recalculate(cur=cursor)

    if category in ('', 'сумма', 'sum'):
        cursor.execute('SELECT player_id, host_elo, elo FROM players WHERE host_elo + elo > 2000 ORDER BY (host_elo + elo) DESC;')
        elo_format = '{host_elo} / {away_elo}'
    elif category in ('хост', 'host', 'первый', 'first'):
        title_format += ' (хост)'
        cursor.execute('SELECT player_id, host_elo, elo FROM players WHERE host_elo > 1050 ORDER BY host_elo DESC;')
        elo_format = '{host_elo}'
    elif category in ('второй', 'away', 'second'):
        title_format += ' (второй)'
        cursor.execute('SELECT player_id, host_elo, elo FROM players WHERE elo > 950 ORDER BY elo DESC;')
        elo_format = '{away_elo}'
    else:
        message = 'Неправильный формат ввода. Попробуйте просто /топ.'
        return [message]

    members_ids = vk_utils.fetch_chat_members_ids(settings.main_chat_id, vk=vk)

    rows = (
        (player_id, host_elo, away_elo)
        for player_id, host_elo, away_elo in cursor
        if player_id in members_ids
    )

    rows = itertools.islice(rows, max_count)

    users_ids, *elos_rows = zip(*rows)

    elos_str = [
        elo_format.format(host_elo=host_elo, away_elo=away_elo)
        for host_elo, away_elo in zip(*elos_rows)
    ]

    count = len(users_ids)

    title = title_format.format(count=count)

    message = f'{title}:\n'

    usernames = vk_utils.fetch_usernames(users_ids, vk=vk)
    for place, (username, elo_str) in enumerate(zip(usernames, elos_str), 1):
        message += f'{place}. {username}: {elo_str} ЭЛО\n'

    return [message]


def _process_top_command(player_id, command_text, *, cursor, vk, **kwargs):
    args = command_text.split()

    count = None
    for arg in tuple(args):
        if _is_int(arg):
            count = int(arg)
            args.remove(arg)
            break
    if count is None:
        count = 10

    if count < 0:
        count = 0

    [category] = args if args else ['sum']

    result = top(count, category=category, cursor=cursor, vk=vk)

    return result


top_command = command_system.Command(
    process=_process_top_command,
    keys=['топ', 'top'],
    description='Игроки с наивысшим ЭЛО-рейтингом',
    signature='(_ / хост / второй)',
    allow_users=True
)
