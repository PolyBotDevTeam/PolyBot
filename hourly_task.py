import elo
import settings
import message_handler
import polybot_utils

from vk_actions import Message


connection = message_handler.create_connection()
with connection:
    cur = connection.cursor()
    cur.execute('SELECT game_id, host_id, away_id, host_winner FROM games WHERE type = \'w\' AND TIMESTAMPDIFF(HOUR, time_updated, NOW()) >= 24;')
    rows = cur.fetchall()
    message = ''
    for game_id, host_id, away_id, host_winner in rows:
        polybot_utils.process_game_finish(game_id, cursor=cur)
        elo.recalculate(cur=cur)
        rating_changes_desc = elo.describe_rating_changes(game_id, cur=cur)
        winner_id = host_id if host_winner else away_id
        mention = message_handler.create_mention(winner_id)
        message += f'Игра №{game_id} завершена в соответствии с заявлением победителя ({mention}).\n{rating_changes_desc}\n\n'
    if message:
        message_handler.send_message(Message(text=message), vk=message_handler.api, chat_id=settings.main_chat_id)
