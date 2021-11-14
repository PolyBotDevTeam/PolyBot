import command_system
import message_handler
import vk_utils


def instawin(player_id, command_text):
    args = command_text.split()
    try:
        winner, game_id = args
        game_id = int(game_id)
    except:
        message = 'Необходимо указать победителя и ID игры в системе.'
        return [message]

    try:
        player_id = vk_utils.id_by_mention(winner)
    except ValueError:
        message = 'Некорректная ссылка. Нажмите @ или * чтобы выбрать среди участников беседы.'
        return [message]

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT host_id, away_id FROM games WHERE game_id = %s AND (type = \'i\' OR type = \'w\' OR type = \'c\') AND (host_id = %s OR away_id = %s);', (game_id, player_id, player_id))
        fetch = cur.fetchone()
        if not fetch:
            message = 'Не найдено игр с указанным ID.'
            return [message]
        [host_id, away_id] = fetch

        host_winner = player_id == host_id
        away_winner = player_id == away_id
        assert host_winner or away_winner

        cur.execute(
            'UPDATE games SET host_winner = %s, type = \'c\', time_updated = NOW() WHERE game_id = %s;',
            (host_winner, game_id)
        )
        cur.execute('SELECT game_id FROM results WHERE game_id = %s;', game_id)
        is_result_inserted = cur.fetchone()
        if is_result_inserted:
            cur.execute(
                'UPDATE results SET host_winner = %s WHERE game_id = %s;',
                (host_winner, game_id)
            )
        else:
            cur.execute(
                'INSERT results(host_id, away_id, host_winner, game_id) VALUES (%s, %s, %s, %s);',
                (host_id, away_id, host_winner, game_id)
            )

        winner_id = host_id if host_winner else away_id

    winner_username = message_handler.username(winner_id)
    message = f'Игра {game_id} завершена, победитель - {winner_username}!'
    return [message]


instawin_command = command_system.AdminCommand()

instawin_command.keys = ['instawin']
instawin_command.description = ' упоминание_игрока ID_игры - Определить победителя игры.'
instawin_command.process = instawin
