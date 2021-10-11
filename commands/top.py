import command_system
import elo as elo_module
import vk_utils


def _is_int(x):
    try:
        int(x)
        result = True
    except ValueError:
        result = False
    return result


def top(count, *, category, cursor, vk):
    title = f'ТОП-{count}'

    elo_module.recalculate(cur=cursor)

    if count == 0:
        ids = []
        elos_str = []
    elif category in ('', 'сумма', 'sum'):
        cursor.execute('SELECT player_id, host_elo, elo FROM players WHERE host_elo + elo > 2000 ORDER BY (host_elo + elo) DESC;')
        rows = cursor.fetchmany(min(count, cursor.rowcount))
        ids, *elos_rows = zip(*rows)
        elos_str = [str(host_elo) + ' / ' + str(away_elo) for host_elo, away_elo in zip(*elos_rows)]
    else:
        if category in ('хост', 'host', 'первый', 'first'):
            title += ' (хост)'
            cursor.execute('SELECT player_id, host_elo FROM players WHERE host_elo > 1050 ORDER BY host_elo DESC;')
        elif category in ('второй', 'away', 'second'):
            title += ' (второй)'
            cursor.execute('SELECT player_id, elo FROM players WHERE elo > 950 ORDER BY elo DESC;')
        else:
            message = 'Неправильный формат ввода. Попробуйте просто /топ.'
            return [message]
        rows = cursor.fetchmany(min(count, cursor.rowcount))
        ids, elos = zip(*rows)
        elos_str = [str(elo) for elo in elos]

    message = f'{title}:\n\n'

    usernames = vk_utils.fetch_usernames(ids, vk=vk)
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
    # TODO: limit = randint(20, 30)?
    if count > 25:
        count = 25
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
