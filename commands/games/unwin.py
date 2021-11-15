import command_system
import message_handler
from db_utils import exists


def unwin(player_id, command_text):
    command_text = command_text.lstrip()
    try:
        game_id = int(command_text)
    except ValueError:
        message = 'Необходимо указать ID игры в системе.'
        return [message]

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()

        cur.execute('SELECT host_id, away_id, type FROM games WHERE game_id = %s;', game_id)
        fetch = cur.fetchone()
        if fetch is None:
            return ['Не найдено игр с указанным ID.', 'Напишите /текущие, чтобы посмотреть список игр с вашим участием.']
        host_id, away_id, game_type = fetch
        del fetch

        if player_id not in (host_id, away_id):
            return ['Вы не участвуете в данной игре.', 'Напишите /текущие, чтобы посмотреть список игр с вашим участием.']

        if game_type != 'w':
            if game_type == 'c':
                message = 'Это победу уже нельзя отменить.'
                hint = 'Если вы считаете, что что-то пошло не так, обратитесь к администратору.'
                return [message, hint]
            elif game_type in ('i', 'o', 'r'):
                message = 'В данной игре ещё никто не победил.'
                return [message]
            else:
                raise RuntimeError('unsupported game type: %s' % game_type)
        assert game_type == 'w'
        assert not exists(cur, 'results', 'game_id = %s', game_id)

        enemy_id = away_id if player_id == host_id else host_id
        enemy_mention = message_handler.create_mention(enemy_id)

        cur.execute('UPDATE games SET host_winner = NULL, type = \'i\', time_updated = NOW() WHERE game_id = %s;', game_id)
        message = f'Победа в игре {game_id} отменена.\n\n{enemy_mention}, если вы не согласны, обратитесь к модератору.'
        return [message]


unwin_command = command_system.UserCommand()

unwin_command.keys = ['отменить_победу', 'отмена_победы', 'непобедил', 'unwin', 'undo_win']
unwin_command.description = ' айди_игры - Отменить победу в игре.'
unwin_command.process = unwin
