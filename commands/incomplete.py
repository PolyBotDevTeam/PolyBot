import command_system
import message_handler
import db_utils


def incomplete(player_id, command_text):
    command_text = command_text.lstrip()
    pointer = command_text if command_text else None
    self = pointer is None

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()

        if pointer is not None:
            try:
                player_id = message_handler.try_to_identify_id(pointer, cur)
            except ValueError:
                message = 'Некорректная ссылка или никнейм. Нажмите @ или * чтобы выбрать среди участников беседы.'
                return [message]
        else:
            player_id = player_id

        anything = db_utils.exists(cur, 'games', "(host_id = %s OR away_id = %s) AND (type = 'o' OR type = 'r' OR type = 'i')", (player_id, player_id))
        if not anything:
            return ['Не найдено текущих игр.']

        message = ''

        cur.execute('SELECT game_id, host_id, away_id, description FROM games WHERE type = \'r\' AND host_id = %s ORDER BY time_updated ASC;', player_id)
        rows = cur.fetchall()
        if rows:
            message += ('Вам' if self else 'Игроку') + ' необходимо начать следующие игры:\n\n'
            for row in rows:
                message += str(row[0]) + ' - ' + message_handler.username(row[1]) + ' vs ' + message_handler.username(row[2]) + '\n' + row[3] + '\n\n'
            message += ' \n'

        cur.execute('SELECT game_id, host_id, away_id, description FROM games WHERE type = \'r\' AND away_id = %s ORDER BY time_updated ASC;', player_id)
        rows = cur.fetchall()
        if rows:
            message += 'Ждём начала игры противником:\n\n'
            for row in rows:
                message += str(row[0]) + ' - ' + message_handler.username(row[1]) + ' vs ' + message_handler.username(row[2]) + '\n' + row[3] + '\n\n'
            message += ' \n'

        cur.execute('SELECT game_id, description FROM games WHERE type = \'o\' AND host_id = %s ORDER BY time_updated ASC;', player_id)
        rows = cur.fetchall()
        if rows:
            message += 'Открытые вами игры:\n\n' if self else 'Открытые игроком игры:\n\n'
            for row in rows:
                message += str(row[0]) + ' - ' + message_handler.username(player_id) + ' vs ___\n' + row[1] + '\n\n'
            message += ' \n'

        cur.execute('SELECT game_id, host_id, away_id, description, name FROM games WHERE type = \'i\' AND (host_id = %s OR away_id = %s) ORDER BY time_updated DESC;', (player_id, player_id))
        rows = cur.fetchall()
        if rows:
            message += 'Текущие игры с вашим участием:\n\n' if self else 'Текущие игры с участием игрока:\n\n'
            for row in rows:
                opponent = row[1] if player_id == row[2] else row[2]
                cur.execute('SELECT nickname FROM players WHERE player_id = %s', (opponent, ))
                (opp_nickname,) = cur.fetchone()
                message += str(row[0]) + ' - ' + str(row[4]) + '\n' + message_handler.username(row[1]) + ' vs ' + message_handler.username(row[2]) + '\n' + row[3] + '\nПротивник: ' + opp_nickname + '\n\n'

        assert message

        return [message]


incomplete_command = command_system.UserCommand()

incomplete_command.keys = ['текущие', 'incomplete']
incomplete_command.description = ' [упоминание игрока] - Незавершённые игры.'
incomplete_command.process = incomplete
