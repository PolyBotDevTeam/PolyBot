import command_system
import message_handler
import utils
import db_utils
import vk_utils


def change_description(player_id, command_text):
    try:
        game_id, command_text = utils.split_one(command_text)
        game_id = int(game_id)
    except ValueError:
        message = 'После команды первым необходимо ввести ID игры.'
        return [message]

    new_description = command_text

    if not new_description:
        return ['Необходимо ввести новое описание игры.']

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()

        try:
            ((host_id, away_id, game_type, old_description),) = db_utils.select(cur, 'SELECT host_id, away_id, type, description FROM games WHERE game_id = %s;', game_id)
        except ValueError:
            return ['Не найдено игр с указанным ID.']

        if player_id != host_id:
            return ['Вы не являетесь создателем этой игры.']

        if game_type not in ('o', 'r'):
            return ['Изменить описание можно только у неначатой игры.']
        assert game_type in ('o', 'r')

        cur.execute('UPDATE games SET description = %s, time_updated = NOW() WHERE game_id = %s;', (new_description, game_id))

    message = f'Описание игры {game_id} успешно изменено.\n\nСтарое описание: {old_description}\n\nНовое описание: {new_description}'
    message = vk_utils.break_mentions(message)
    if away_id is not None:
        message += f'\n\n{message_handler.create_mention(away_id)}, не пропустите изменения.'

    return [message]


change_description_command = command_system.UserCommand()

change_description_command.keys = ['изменить_описание', 'change_description']
change_description_command.description = ' ID_игры новое_описание - Изменить описание игры.'
change_description_command.process = change_description
