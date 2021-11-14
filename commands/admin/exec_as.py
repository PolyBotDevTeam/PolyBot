import command_system
import utils
import vk_utils


def _process_exec_as_command(player_id, command_text, **kwargs):
    command_text = command_text.lstrip()
    try:
        player_link, command_to_exec_str = utils.split_one(command_text)
    except ValueError:
        message = 'Необходимо указать пользователя и команду.'
        return [message]

    try:
        target_player_id = vk_utils.id_by_mention(player_link)
    except vk_utils.InvalidMentionError:
        message = 'Некорректная ссылка. Нажмите @ или * чтобы выбрать среди участников беседы.'
        return [message]

    command_info, command_text = command_system.split_command_and_arguments(command_to_exec_str)
    try:
        command_to_exec = command_system.get_command(command_info)
    except command_system.CommandNotFoundError:
        return [f'Команда с именем "{command_info}" не найдена.']

    return command_to_exec(target_player_id, command_text, **kwargs)


exec_as_command = command_system.Command(
    process=_process_exec_as_command,
    keys=['exec_as', 'as'],
    description='Выполнить команду от лица указанного игрока',
    signature='упоминание_игрока команда',
    allow_users=False
)
