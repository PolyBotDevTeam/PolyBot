import command_system
import db_utils
import elo


def instadel(player_id, command_text, *, database, **kwargs):
    args = command_text.split()
    if not args:
        message = 'Необходимо ввести ID игры которую нужно удалить.'
        return [message]
    game_id, *args = args

    mode = 'hard'  # TODO: make soft by default, not hard
    if args:
        try:
            (mode,) = args
        except ValueError:
            return ['Слишком много аргументов.']
        if mode not in ('soft', 'hard'):
            return ['Несуществующий режим команды.']
    del args

    if mode == 'soft':
        # TODO: new 'd' type is not supported yet by other commands
        return ['soft mode не поддерживается на данный момент.']

    connection = database.create_connection()
    with connection:
        cur = connection.cursor()
        if not db_utils.exists(cur, 'games', 'game_id = %s', game_id):
            return ['Не игр с указанным ID.']
        if mode == 'hard':
            cur.execute('DELETE FROM games WHERE game_id = %s;', game_id)
            message = 'Игра успешно стёрта.'
        else:
            assert mode == 'soft'
            cur.execute("UPDATE games SET type = 'd' WHERE game_id = %s;", game_id)
            message = 'Игра успешно удалена.'
        if db_utils.exists(cur, 'results', 'game_id = %s', game_id):
            cur.execute('DELETE FROM results WHERE game_id = %s;', game_id)
            message += ' Также %s результат игры.' % ('стёрт' if mode == 'hard' else 'удалён')

    elo.recalculate(database=database)

    return [message]


instadel_command = command_system.Command(
    process=instadel,
    keys=['instadel'],
    description='Удалить игру',
    signature='ID_игры',
    allow_users=False
)
