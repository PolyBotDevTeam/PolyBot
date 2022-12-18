import command_system
import elo
import polybot_utils
import vk_utils


def _process_command(actor_id, command_text, *, connection, vk, **kwargs):
    cursor = connection.cursor()
    cursor.execute('SELECT game_id, host_id, away_id, host_winner FROM games WHERE type = \'w\' AND TIMESTAMPDIFF(HOUR, time_updated, NOW()) >= 24;')
    message = ''
    for game_id, host_id, away_id, host_winner in tuple(cursor):
        polybot_utils.process_game_finish(game_id, cursor=connection.cursor())
        rating_changes_desc = elo.describe_rating_changes(game_id, cur=connection.cursor())
        winner_id = host_id if host_winner else away_id
        mention = vk_utils.create_mention(winner_id, vk=vk)
        message += f'Игра №{game_id} завершена в соответствии с заявлением победителя ({mention}).\n{rating_changes_desc}\n\n'

    if message:
        yield message


autoconfirm_outdated_wins_command = command_system.Command(
    process=_process_command,
    keys=['autoconfirm_outdated_wins'],
    description='Автоматически подтвердить все проигнорированные заявления о победе',
    signature='',
    allow_users=False
)
