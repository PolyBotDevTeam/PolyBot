import db_utils
from user_errors import UserError
import string
import utils


# TODO: win/etc.?
#       move repeating code here?


# TODO: associations?
def game_id_by_message(message, *, cursor):
    text = message['text']
    i = 0
    numbers = []
    while i < len(text):
        while i < len(text) and text[i] not in string.digits:
            i += 1
        if i < len(text):
            numbers.append('')
        while i < len(text) and text[i] in string.digits:
            numbers[-1] += text[i]
            i += 1
    numbers = tuple(map(int, numbers))
    valid_ids = [gid for gid in numbers if db_utils.exists(cursor, 'games', 'game_id = %s AND TIMESTAMPDIFF(HOUR, time_updated, NOW()) <= 24*365;', gid)]
    if len(valid_ids) > 1:
        raise ValueError('two games ids found')
    try:
        [game_id] = valid_ids
    except ValueError:
        raise ValueError
    return game_id


def try_take_game_id(command_text, actor_message, *, cursor):
    if 'reply_message' not in actor_message.keys():
        try:
            game_id, command_text = utils.split_one(command_text)
            game_id = int(game_id)
        except ValueError:
            raise UserError('После команды первым необходимо ввести ID игры.')
    else:
        try:
            game_id = game_id_by_message(actor_message['reply_message'], cursor=cursor)
        except ValueError:
            raise UserError('Не удалось определить ID игры по указанному сообщению.')
    return game_id, command_text


def is_game_name_correct(game_name):
    chars_used = set(game_name)
    chars_allowed = set(string.ascii_letters + ' &-')
    return chars_used.issubset(chars_allowed) and 0 < len(game_name) <= 30


def process_game_finish(game_id, *, cursor):
    cursor.execute('SELECT EXISTS(SELECT * FROM games WHERE game_id = %s);', game_id)
    [[game_exists]] = cursor
    if not game_exists:
        raise ValueError('the game with this id does not exist')

    cursor.execute('SELECT type, is_rated, host_id, away_id, host_winner FROM games WHERE game_id = %s;', game_id)
    [[game_type, is_rated, host_id, away_id, host_winner]] = cursor

    if game_type not in ('w', 'c'):
        raise ValueError('the game is unfinished')

    cursor.execute('UPDATE games SET type = \'c\', time_updated = NOW() WHERE game_id = %s;', game_id)

    cursor.execute(
        'SELECT EXISTS(SELECT * FROM results WHERE game_id = %s);',
        game_id
    )
    [[is_result_inserted]] = cursor

    if is_result_inserted:
        cursor.execute(
            'UPDATE results SET host_winner = %s, is_rated = %s WHERE game_id = %s;',
            (host_winner, is_rated, game_id)
        )
    else:
        cursor.execute(
            'INSERT results(host_id, away_id, host_winner, is_rated, game_id) VALUES (%s, %s, %s, %s, %s);',
            (host_id, away_id, host_winner, is_rated, game_id)
        )
