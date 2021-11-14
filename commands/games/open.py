import command_system
import vk_utils


def _process_open_command(actor_id, command_text, *, database, cursor, **kwargs):
    description = command_text
    if not description:
        message = 'Необходимо ввести описание игры. Это может быть имя игрока с которым вы хотите сыграть, минимальный/максимальный рейтинг для вступления, какие-либо дополнительные правила на ваше усмотрение. По умолчанию игра создаётся на карте размера Normal в режиме Might.'
        return [message]

    players = database.players
    cur = cursor

    if not players.is_registered(actor_id):
        message = 'Вы не зарегистрированы в системе. Воспользуйтесь командой /гайд, чтобы узнать о работе бота.'
        return [message]

    cur.execute('SELECT game_id FROM games WHERE host_id = %s AND type = \'r\'', actor_id)
    fetch = cur.fetchone()
    if fetch:
        ready = fetch[0]
        if ready:
            message = f'Нельзя открыть игру. Игра {ready} ждёт своего начала. Создайте игру в Политопии и используйте команду /начать ID_игры название_игры, чтобы получить возможность открывать новые игры.'
            return [message]

    cur.execute('SELECT COUNT(1) FROM games WHERE host_id = %s AND type = \'o\'', actor_id)
    opened = cur.fetchone()[0]
    if opened > 2:
        message = 'Вы уже открыли 3 игры. Подождите их заполнения, перед тем как открывать новые.'
        return [message]

    cur.execute('INSERT games(type, host_id, description, time_updated) VALUES (\'o\', %s, %s, NOW());', (actor_id, description))
    cur.execute('SELECT MAX(game_id) FROM games')
    new_id = cur.fetchone()[0]

    message = f'Игра успешно открыта.\nID игры в системе: {new_id}\nОписание: {description}'
    message = vk_utils.break_mentions(message)
    return [message]


open_command = command_system.Command(
    process=_process_open_command,
    keys=['открыть', 'создать', 'open'],
    description='Создать игру с вами в роли хоста. Другие игроки смогут вступить в неё',
    signature='описание',
    allow_users=True
)
