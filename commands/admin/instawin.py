import command_system
import polybot_utils
import vk_utils


def instawin(player_id, command_text, *, database, vk, **kwargs):
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

    connection = database.create_connection()
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
        polybot_utils.process_game_finish(game_id, cursor=cur)

    winner_id = host_id if host_winner else away_id
    winner_username = vk_utils.fetch_username(winner_id, vk=vk)
    message = f'Игра {game_id} завершена, победитель - {winner_username}!'
    return [message]


instawin_command = command_system.Command(
    process=instawin,
    keys=['instawin'],
    description='Определить победителя игры',
    signature='упоминание_игрока ID_игры',
    allow_users=False
)
