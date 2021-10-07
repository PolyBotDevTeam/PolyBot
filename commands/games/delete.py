import command_system
import message_handler


def delete(player_id, command_text):
    args = command_text.split()
    if len(args) != 1:
        if len(args) == 0:
            message = 'Необходимо ввести ID игры, которую нужно удалить.'
        elif len(args) >= 2:
            message = 'Слишком много параметров. Необходимо ввести только ID игры, которую нужно удалить.'
        return [message]
    (game_id,) = args
    game_id = int(game_id)

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT game_id FROM games WHERE game_id = %s AND (type = \'o\' OR type = \'r\') AND host_id = %s;', (game_id, player_id))
        fetch = cur.fetchone()
        if not fetch:
            message = 'Не найдено открытых или готовых к старту игр с указанным ID.'
            return [message]
        cur.execute('DELETE FROM games WHERE game_id = %s;', (game_id, ))
        message = 'Игра успешно удалена.'
        return [message]


delete_command = command_system.UserCommand()

delete_command.keys = ['удалить', 'delete']
delete_command.description = ' ID_игры - Исключить противника из вашей ещё не стартовавшей игры.'
delete_command.process = delete
