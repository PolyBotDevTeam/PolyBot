import command_system
import message_handler
import elo as elo_module


def _is_int(x):
    try:
        int(x)
        result = True
    except ValueError:
        result = False
    return result


def top(player_id, command_text):
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

    title = f'ТОП-{count}'

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()
        elo_module.recalculate(cur=cur)

        if count == 0:
            ids = []
            elos_str = []
        elif not args:
            cur.execute('SELECT player_id, host_elo, elo FROM players WHERE host_elo + elo > 2000 ORDER BY (host_elo + elo) DESC;')
            rows = cur.fetchmany(min(count, cur.rowcount))
            ids, *elos_rows = zip(*rows)
            elos_str = [str(host_elo) + ' / ' + str(away_elo) for host_elo, away_elo in zip(*elos_rows)]
        else:
            if args[0] in ('хост', 'host', 'первый', 'first'):
                title += ' (хост)'
                cur.execute('SELECT player_id, host_elo FROM players WHERE host_elo > 1050 ORDER BY host_elo DESC;')
            elif args[0] in ('второй', 'away', 'second'):
                title += ' (второй)'
                cur.execute('SELECT player_id, elo FROM players WHERE elo > 950 ORDER BY elo DESC;')
            else:
                message = 'Неправильный формат ввода. Попробуйте просто /топ.'
                return [message]
            rows = cur.fetchmany(min(count, cur.rowcount))
            ids, elos = zip(*rows)
            elos_str = [str(elo) for elo in elos]

    message = f'{title}:\n\n'

    usernames = message_handler.fetch_usernames(ids)
    for place, (username, elo_str) in enumerate(zip(usernames, elos_str), 1):
        message += f'{place}. {username}: {elo_str} ЭЛО\n'

    return [message]


top_command = command_system.UserCommand()

top_command.keys = ['топ', 'top']
top_command.description = ' (_ / хост / второй) - Игроки с наивысшим ЭЛО-рейтингом.'
top_command.process = top
