import command_system
import message_handler
import db_utils
import vk_utils


def _process_incomplete_command(player_id, command_text, *, vk, **kwargs):
    command_text = command_text.lstrip()
    pointer = command_text if command_text else None
    self = pointer is None

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()

        if pointer is not None:
            try:
                player_id = message_handler.try_to_identify_id(pointer, cur)
            except ValueError:
                message = 'Некорректная ссылка или никнейм. Нажмите @ или * чтобы выбрать среди участников беседы.'
                return [message]
        else:
            player_id = player_id

        anything = db_utils.exists(cur, 'games', "(host_id = %s OR away_id = %s) AND (type = 'o' OR type = 'r' OR type = 'i')", (player_id, player_id))
        if not anything:
            return ['Не найдено текущих игр.']

        message = ''

        cur.execute('SELECT game_id, host_id, away_id, description FROM games WHERE type = \'r\' AND host_id = %s ORDER BY time_updated ASC;', player_id)
        rows = cur.fetchall()
        if rows:
            message += ('Вам' if self else 'Игроку') + ' необходимо начать следующие игры:\n\n'
            for game_id, host_id, away_id, description in rows:
                host_username = vk_utils.fetch_username(host_id, vk=vk)
                away_username = vk_utils.fetch_username(away_id, vk=vk)
                message += f'{game_id} - {host_username} vs {away_username}\n{description}\n\n'
            message += ' \n'

        cur.execute('SELECT game_id, host_id, away_id, description FROM games WHERE type = \'r\' AND away_id = %s ORDER BY time_updated ASC;', player_id)
        rows = cur.fetchall()
        if rows:
            message += 'Ждём начала игры противником:\n\n'
            for game_id, host_id, away_id, description in rows:
                host_username = vk_utils.fetch_username(host_id, vk=vk)
                away_username = vk_utils.fetch_username(away_id, vk=vk)
                message += f'{game_id} - {host_username} vs {away_username}\n{description}\n\n'
            message += ' \n'

        cur.execute('SELECT game_id, description FROM games WHERE type = \'o\' AND host_id = %s ORDER BY time_updated ASC;', player_id)
        rows = cur.fetchall()
        if rows:
            message += 'Открытые вами игры:\n\n' if self else 'Открытые игроком игры:\n\n'
            command_target_username = vk_utils.fetch_username(player_id, vk=vk)
            for game_id, description in rows:
                message += f'{game_id} - {command_target_username} vs ___\n{description}\n\n'
            message += ' \n'

        cur.execute('SELECT game_id, host_id, away_id, description, name FROM games WHERE type = \'i\' AND (host_id = %s OR away_id = %s) ORDER BY time_updated DESC;', (player_id, player_id))
        rows = cur.fetchall()
        if rows:
            message += 'Текущие игры с вашим участием:\n\n' if self else 'Текущие игры с участием игрока:\n\n'
            for game_id, host_id, away_id, description, game_name in rows:
                host_username = vk_utils.fetch_username(host_id, vk=vk)
                away_username = vk_utils.fetch_username(away_id, vk=vk)
                opponent = host_id if player_id == away_id else away_id
                cur.execute('SELECT nickname FROM players WHERE player_id = %s', opponent)
                (opp_nickname,) = cur.fetchone()
                message += f'{game_id} - {game_name}\n{host_username} vs {away_username}\n{description}\nПротивник: {opp_nickname}\n\n'

        assert message

        return [message]


incomplete_command = command_system.Command(
    process=_process_incomplete_command,
    keys=['текущие', 'incomplete'],
    description='Активные игры с вашим участием',
    signature='[упоминание_игрока]',
    allow_users=True
)
