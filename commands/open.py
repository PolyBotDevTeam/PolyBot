import command_system
import message_handler
import utils


def open(player_id, command_text):
    description = command_text.lstrip()
    if not description:
        message = 'Необходимо ввести описание игры. Это может быть имя игрока с которым вы хотите сыграть, минимальный/максимальный рейтинг для вступления, какие-либо дополнительные правила на ваше усмотрение. По умолчанию игра создаётся на карте размера Normal в режиме Might.'
        return [message]
    description = utils.delete_mentions(description)

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()

        cur.execute('SELECT player_id FROM players WHERE player_id = %s', (player_id,))
        fetch = cur.fetchone()
        if not fetch:
            message = 'Вы не зарегистрированы в системе. Воспользуйтесь командой /гайд, чтобы узнать о работе бота.'
            return [message]

        cur.execute('SELECT game_id FROM games WHERE host_id = %s AND type = \'r\'', (player_id,))
        fetch = cur.fetchone()
        if fetch:
            ready = fetch[0]
            if ready:
                message = f'Нельзя открыть игру. Игра {ready} ждёт своего начала. Создайте игру в Политопии и используйте команду /начать ID_игры название_игры, чтобы получить возможность открывать новые игры.'
                return [message]

        cur.execute('SELECT COUNT(1) FROM games WHERE host_id = %s AND type = \'o\'', (player_id,))
        opened = cur.fetchone()[0]
        if opened > 2:
            message = 'Вы уже открыли 3 игры. Подождите их заполнения, перед тем как открывать новые.'
            return [message]

        cur.execute('INSERT games(type, host_id, description, time_updated) VALUES (\'o\', %s, %s, NOW());', (player_id, description))
        cur.execute('SELECT MAX(game_id) FROM games')
        new_id = cur.fetchone()[0]
        message = f'Игра успешно открыта.\nID игры в системе: {new_id}\nОписание: {description}'
        return [message]


open_command = command_system.UserCommand()

open_command.keys = ['открыть', 'создать', 'open']
open_command.description = ' описание - Создать игру с вами в роли хоста. Другие игроки смогут вступить в неё.'
open_command.process = open
