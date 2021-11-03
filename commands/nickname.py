import command_system
import message_handler


def show_nickname(actor_id, command_text, *, cursor, database, actor_message, **kwargs):
    if command_text:
        try:
            target_player_id = message_handler.try_to_identify_id(command_text, cursor)
        except ValueError:
            # TODO: Can find at least 3 such messages in this project.
            #       Probably should move it out.
            return ['Не удалось обнаружить пользователя по введённым данным.']

    elif actor_message is not None and 'reply_message' in actor_message.keys():
        target_player_id = actor_message['reply_message']['from_id']

    else:
        target_player_id = actor_id

    if not database.players.is_registered(target_player_id):
        if target_player_id == actor_id:
            message = 'Вы ещё не зарегистрированы в системе. Воспользуйтесь командой /гайд или /помощь регистрация'
        else:
            message = 'Этот пользователь ещё не зарегистрирован в системе.'
        return [message]

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
