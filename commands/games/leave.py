import command_system
import message_handler


def leave(player_id, command_text):
    args = command_text.split()
    if not args:
        message = 'Необходимо ввести ID игры, из которой нужно выйти.'
        return [message]
    if len(args) > 1:
        message = 'Слишком много параметров. Необходимо ввести только ID игры, из которой нужно выйти.'
        return [message]
    (game_id,) = args
    game_id = int(game_id)

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT game_id FROM games WHERE game_id = %s AND type = \'r\' AND away_id = %s;', (game_id, player_id))
        fetch = cur.fetchone()
        if not fetch:
            message = 'Не найдено готовых к старту игр с указанным ID.'
            return [message]
        cur.execute('UPDATE games SET away_id = NULL, type = \'o\', time_updated = NOW() WHERE game_id = %s;', (game_id, ))
        message = 'Вы вышли из игры %s.' % game_id
        return [message]


leave_command = command_system.UserCommand()

leave_command.keys = ['выйти', 'покинуть', 'leave']
leave_command.description = ' ID_игры - Выйти из ещё не стартовавшей игры.'
leave_command.process = leave
