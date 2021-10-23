import command_system
import db_utils
import message_handler


def show_nickname(actor_id, command_text, *, cursor, actor_message, **kwargs):
    if command_text:
        try:
            target_player_id = message_handler.try_to_identify_id(command_text, cursor)
        except ValueError:
            target_player_id = None
        if target_player_id is None or not db_utils.exists(cursor, 'players', 'player_id = %s', target_player_id):
            # TODO: Can find at least 3 such messages in this project.
            #       Probably should move it out.
            return ['Не удалось обнаружить пользователя по введённым данным.']

    elif actor_message is not None and 'reply_message' in actor_message.keys():
        target_player_id = actor_message['reply_message']['from_id']

    else:
        target_player_id = actor_id

    cursor.execute('SELECT nickname FROM players WHERE player_id = %s;', target_player_id)
    [[nickname]] = cursor
    return [nickname]


nickname_command = command_system.Command(
    process=show_nickname,
    keys=['ник', 'никнейм', 'nick', 'nickname'],
    description='Узнать игровой никнейм игрока',
    signature='игрок',
    allow_users=True
)
