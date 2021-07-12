import command_system
import utils
import vk_utils


def exec_as(player_id, command_text):
    command_text = command_text.lstrip()
    try:
        player_link, command_to_exec = utils.split_one(command_text)
    except ValueError:
        message = 'Необходимо указать пользователя и команду.'
        return [message]

    try:
        target_player_id = vk_utils.id_by_mention(player_link)
    except vk_utils.InvalidMentionError:
        message = 'Некорректная ссылка. Нажмите @ или * чтобы выбрать среди участников беседы.'
        return [message]

    command_name, command_text = command_system.preprocess_command(command_to_exec, '/')
    user_commands = command_system.user_commands
    if not user_commands.has_command(command_name):
        return ['Команда с таким именем не найдена.']
    c = user_commands.get_command(command_name)

    return c.process(target_player_id, command_text)


exec_as_command = command_system.AdminCommand()

exec_as_command.keys = ['exec_as', 'as']
exec_as_command.description = ' упоминание_игрока команда - Выполнить команду от лица указанного игрока.'
exec_as_command.process = exec_as
