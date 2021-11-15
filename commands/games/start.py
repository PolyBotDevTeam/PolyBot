import command_system
import message_handler
import polybot_utils
import utils
import vk_utils


def start(player_id, command_text):
    command_text = command_text
    try:
        game_id, name = utils.split_one(command_text)
        game_id = int(game_id)
    except:
        message = 'После имени команды необходимо ввести ID игры, а затем её название в Политопии.'
        return [message]

    if not name:
        return ['После айди игры необходимо ввести название игры в Политопии.']
    if not polybot_utils.is_game_name_correct(name):
        message = 'Пожалуйста, введите именно то название игры, которое указано в Политопии.'
        return [message]

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT away_id FROM games WHERE game_id = %s AND type = \'r\' AND host_id = %s;', (game_id, player_id))
        fetch = cur.fetchone()
        if not fetch:
            message = 'Не найдено ваших ожидающих начала игр с указанным ID.'
            return [message]
        (away_id,) = fetch
        del fetch
        cur.execute('UPDATE games SET name = %s, type = \'i\', time_updated = NOW() WHERE game_id = %s;', (name, game_id))

    name = vk_utils.break_mentions(name)
    message = f'Игра {game_id} успешно создана.\n\n{message_handler.create_mention(away_id)}, в ближайшее время вы будете приглашены в игру {name}.'
    return [message]


start_command = command_system.UserCommand()

start_command.keys = ['начать', 'старт', 'start']
start_command.description = ' айди_игры название_игры_в_политопии - Начать заполненную игру. Перед применением команды начните игру в Политопии и укажите здесь её название.'
start_command.process = start
