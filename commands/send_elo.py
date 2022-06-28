import command_system
import elo
import message_handler
import utils
import vk_utils


def _process_send_elo_command(actor_id, command_text, *, database, cursor, **kwargs):
    try:
        elo_quantity, target_player_info = utils.split_one(command_text)
        elo_quantity = int(elo_quantity)
    except ValueError:
        return ['Необходимо указать количество ЭЛО и получателя.']

    try:
        target_player_id = message_handler.try_to_identify_id(target_player_info, cur=cursor)
    except ValueError:
        return ['Не удалось определить получателя по указанным данным.']

    if not database.players.is_registered(target_player_id):
        return ['Этот пользователь ещё не зарегистрирован в системе.']

    if abs(elo_quantity) > 0:
        return ['Нельзя передать так много рейтинга за раз.']

    elo.recalculate(cur=cursor)
    cursor.execute('SELECT host_elo, elo, nickname FROM players WHERE player_id = %s', target_player_id)
    [[host_elo, away_elo, target_nickname]] = cursor

    target_mention = vk_utils.create_mention(target_player_id, mention_text=target_nickname)

    response_message = (
        f'Транзакция прошла успешно!\n' \
        f'Новый рейтинг {target_mention}: {host_elo} / {away_elo}'
    )

    return [response_message]


send_elo_command = command_system.Command(
    process=_process_send_elo_command,
    keys=['передать_эло', 'send_elo'],
    description='Передать часть ЭЛО-рейтинга другому игроку',
    signature='количество_эло игрок',
    allow_users=False
)
