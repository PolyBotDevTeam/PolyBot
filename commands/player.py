import command_system
import message_handler
import elo
import vk_utils
import db_utils


def _process_player_command(actor_id, command_text, *, cursor, **kwargs):
    player_to_describe_info = command_text if command_text else None
    del command_text

    if player_to_describe_info is not None:
        try:
            player_to_describe_id = message_handler.try_to_identify_id(player_to_describe_info, cursor)
        except vk_utils.InvalidMentionError:
            return ['Некорректная ссылка. Нажмите @ или *, чтобы выбрать среди участников беседы.']
        except ValueError:
            return ['Не удалось обнаружить пользователя по введённым данным.']
    else:
        player_to_describe_id = actor_id

    if not db_utils.exists(cursor, 'players', 'player_id = %s', player_to_describe_id):
        if player_to_describe_id == actor_id:
            message = 'Вы ещё не зарегистрированы в системе.'
        else:
            message = 'Этот пользователь ещё не зарегистрирован в системе.'
        return [message]

    elo.recalculate(cur=cursor)
    message = _compose_description(player_to_describe_id, cursor)
    return [message]


def _compose_description(player_id, cursor):
    cursor.execute('SELECT player_id, role, host_elo, elo, nickname, joining_time FROM players WHERE player_id = %s', player_id)
    _player_id, role, elo_host, elo_away, nickname, joining_time = cursor.fetchone()
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
