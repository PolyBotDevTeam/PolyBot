import command_system
import message_handler
import db_utils
import vk_utils


def _process_incomplete_command(actor_id, command_text, *, vk, cursor, **kwargs):
    cur = cursor

    specified_player = command_text if command_text else None

    if specified_player is None:
        player_id = actor_id
    else:
        try:
            player_id = message_handler.try_to_identify_id(specified_player, cur)
        except ValueError:
            message = 'Некорректная ссылка или никнейм. Нажмите @ или * чтобы выбрать среди участников беседы.'
            return [message]

    is_self = player_id == actor_id

    message = ''

    cur.execute('SELECT game_id, host_id, away_id, description FROM games WHERE type = \'r\' AND host_id = %s ORDER BY time_updated ASC;', player_id)
    rows = cur.fetchall()
    if rows:
        message += ('Вам' if is_self else 'Игроку') + ' необходимо начать следующие игры:\n\n'
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
        message += 'Открытые вами игры:\n\n' if is_self else 'Открытые игроком игры:\n\n'
        command_target_username = vk_utils.fetch_username(player_id, vk=vk)
        for game_id, description in rows:
            message += f'{game_id} - {command_target_username} vs ___\n{description}\n\n'
        message += ' \n'

    cur.execute('SELECT game_id, host_id, away_id, description, name FROM games WHERE type = \'i\' AND (host_id = %s OR away_id = %s) ORDER BY time_updated DESC;', (player_id, player_id))
    rows = cur.fetchall()
    if rows:
        message += 'Текущие игры с вашим участием:\n\n' if is_self else 'Текущие игры с участием игрока:\n\n'
        for game_id, host_id, away_id, description, game_name in rows:
            host_username = vk_utils.fetch_username(host_id, vk=vk)
            away_username = vk_utils.fetch_username(away_id, vk=vk)
            opponent = host_id if player_id == away_id else away_id
            cur.execute('SELECT nickname FROM players WHERE player_id = %s', opponent)
            [opponent_nickname] = cur.fetchone()
            message += f'{game_id} - {game_name}\n{host_username} vs {away_username}\n{description}\nПротивник: {opponent_nickname}\n\n'

    if not message:
        message = 'Не найдено текущих игр.'

    return [message]


incomplete_command = command_system.Command(
    process=_process_incomplete_command,
    keys=['текущие', 'incomplete'],
    description='Активные игры с вашим участием',
    signature='[упоминание_игрока]',
    allow_users=True
)
