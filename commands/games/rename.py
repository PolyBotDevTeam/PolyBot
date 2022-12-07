import command_system
import message_handler
import polybot_utils
import utils
import db_utils
import vk_utils


def rename(player_id, command_text):
    try:
        game_id, command_text = utils.split_one(command_text)
        game_id = int(game_id)
    except ValueError:
        message = 'После имени команды необходимо ввести ID игры, а затем её название в Политопии.'
        return [message]

    new_game_name = command_text
    if not new_game_name:
        return ['После айди игры необходимо ввести название игры в Политопии.']
    if not polybot_utils.is_game_name_correct(new_game_name):
        return ['Пожалуйста, введите именно то название игры, которое указано в Политопии.']

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()

        try:
            [[host_id, away_id, game_type, old_game_name]] = db_utils.execute(cur, 'SELECT host_id, away_id, type, name FROM games WHERE game_id = %s;', game_id)
        except ValueError:
            return ['Не найдено игр с указанным ID.']

        if player_id != host_id:
            return ['Вы не являетесь создателем этой игры.']

        if game_type != 'i':
            response = ['Изменять названия можно только у идущих игр.']
            if game_type in ('o', 'r'):
                hint = 'Вы можете воспользоваться командой /изменить_описание'
                if game_type == 'r':
                    hint += f'.\nИли начать игру командой /начать {game_id} название_игры_в_политопии'
                response.append(hint)
            return response
        assert game_type == 'i'

        cur.execute(f'UPDATE games SET name = %s, time_updated = NOW() WHERE game_id = %s;', (new_game_name, game_id))

    old_game_name = vk_utils.break_mentions(old_game_name)
    new_game_name = vk_utils.break_mentions(new_game_name)
    message = f'Игра {game_id} успешно переименована.\n\n{message_handler.create_mention(away_id)}, в ближайшее время вы будете приглашены в игру {new_game_name}, из старой игры ({old_game_name}) можно выйти.'
    return [message]


rename_command = command_system.UserCommand()

rename_command.keys = ['переименовать', 'rename', 'рестарт', 'restart']
rename_command.description = ' ID_игры название_игры_в_политопии - Переименовать идущую игру. Использовать после каждого рестарта.'
rename_command.process = rename
