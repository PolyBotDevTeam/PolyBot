import command_system
import message_handler


def kick(player_id, command_text):
    args = command_text.split()
    if not args:
        message = 'Необходимо ввести ID игры, из которой нужно кикнуть игрока.'
        return [message]
    if len(args) > 1:
        message = 'Слишком много параметров. Необходимо ввести только ID игры, из которой нужно кикнуть игрока.'
        return [message]
    (game_id,) = args
    game_id = int(game_id)

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT away_id FROM games WHERE game_id = %s AND type = \'r\' AND host_id = %s;', (game_id, player_id))
        fetch = cur.fetchone()
        if not fetch:
            message = 'Не найдено готовых к старту игр с указанным ID.'
            return [message]
        cur.execute('UPDATE games SET away_id = NULL, type = \'o\', time_updated = NOW() WHERE game_id = %s;', (game_id, ))
        message = '{0} был удалён из игры {1}.'.format(message_handler.username(fetch[0]), game_id)
        return [message]


kick_command = command_system.UserCommand()

kick_command.keys = ['кикнуть', 'исключить', 'kick']
kick_command.description = ' ID_игры - Исключить противника из вашей ещё не стартовавшей игры.'
kick_command.process = kick
