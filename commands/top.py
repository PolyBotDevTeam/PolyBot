import command_system
import elo as elo_module
import itertools
import settings
import utils
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
        cursor.execute('SELECT player_id, host_elo, elo FROM players WHERE host_elo + elo >= 2000 ORDER BY (host_elo + elo) DESC;')
        top_item_template = '{place}. {host_emoji}{away_emoji} {username}: {host_elo} / {away_elo} ЭЛО\n'
    elif category in ('хост', 'host', 'первый', 'first'):
        title_format += ' (хост)'
        cursor.execute('SELECT player_id, host_elo, elo FROM players WHERE host_elo >= 1050 ORDER BY host_elo DESC;')
        top_item_template = '{place}. {host_emoji} {username}: {host_elo} ЭЛО\n'
    elif category in ('второй', 'away', 'second'):
        title_format += ' (второй)'
        cursor.execute('SELECT player_id, host_elo, elo FROM players WHERE elo >= 950 ORDER BY elo DESC;')
        top_item_template = '{place}. {away_emoji} {username}: {away_elo} ЭЛО\n'
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
    users_ids, *elos_rows = utils.safe_zip(*rows, result_length=3)
    count = len(users_ids)
    usernames = vk_utils.fetch_usernames(users_ids, vk=vk)

    title = title_format.format(count=count)

    message = f'{title}:\n'

    for place, (username, host_elo, away_elo) in enumerate(zip(usernames, *elos_rows), 1):
        digits_n = len(str(count))
        numeric_space = '\u2007'
        place = str(place).ljust(digits_n, numeric_space)

        host_emoji, away_emoji = elo_module.emoji_by_elo(host_elo, away_elo)

        top_item = top_item_template.format(
            place=place,
            username=username,
            host_elo=host_elo,
            away_elo=away_elo,
            host_emoji=host_emoji,
            away_emoji=away_emoji
        )

        message += top_item

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

    max_count = 20
    if count > max_count:
        count = max_count

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
