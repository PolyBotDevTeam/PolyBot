import command_system
import message_handler
import elo
import vk_utils
import db_utils


def _process_player_command(actor_id, command_text, *, cursor, **kwargs):
    player_called_id = actor_id
    del actor_id

    pointer = command_text if command_text else None
    del command_text

    cur = cursor

    try:
        player_to_desc_id = message_handler.try_to_identify_id(pointer, cur) if pointer is not None else player_called_id
    except vk_utils.InvalidMentionError:
        message = 'Некорректная ссылка. Нажмите @ или *, чтобы выбрать среди участников беседы.'
        return [message]
    except ValueError:
        message = 'Не удалось обнаружить пользователя по введённым данным.'
        return [message]

    if not db_utils.exists(cur, 'players', 'player_id = %s', player_to_desc_id):
        if pointer is None:
            message = 'Вы ещё не зарегистрированы в системе.'
        else:
            message = 'Этот пользователь ещё не зарегистрирован в системе.'
        return [message]

    elo.recalculate(cur=cur)
    message = _compose_description(player_to_desc_id, cur)
    return [message]


def _compose_description(player_id, cur):
    cur.execute('SELECT player_id, role, host_elo, elo, nickname, joining_time FROM players WHERE player_id = %s', player_id)
    _player_id, role, elo_host, elo_away, nickname, joining_time = cur.fetchone()
    username = message_handler.username(player_id)
    role = role if role is not None else 'Игрок'
    desc = f'{username} - {role}\nЭЛО: {elo_host} : {elo_away}\nНикнейм: {nickname}\nДата регистрации: {joining_time}'
    return desc


player_command = command_system.Command(
    process=_process_player_command,
    keys=['игрок', 'player'],
    description='Подробная информация об игроке',
    signature='никнейм_игрока (или имя и фамилия, или ссылка на его профиль в формате @ссылка)',
    allow_users=True
)
