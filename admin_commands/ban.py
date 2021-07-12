import command_system
import vk_utils
import message_handler


def ban(player_id, command_text):
    pointer = command_text.lstrip()
    if not pointer:
        message = 'Укажите пользователя.'
        return [message]

    try:
        player_id = vk_utils.id_by_mention(pointer)
    except vk_utils.InvalidMentionError:
        message = 'Некорректная ссылка. Нажмите @ или * чтобы выбрать среди участников беседы.'
        return [message]

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT EXISTS(SELECT player_id FROM players WHERE player_id = %s)', (player_id,))
        if not cur.fetchone()[0]:
            message = 'Этот пользователь ещё не зарегистрирован в системе.'
            return [message]
        cur.execute('UPDATE players SET banned = 1 WHERE player_id = %s', (player_id, ))
        message = 'Пользователь забанен.'
        return [message]


ban_command = command_system.AdminCommand()

ban_command.keys = ['ban']
ban_command.description = ' упоминание - Бан пользователя в системе.'
ban_command.process = ban
