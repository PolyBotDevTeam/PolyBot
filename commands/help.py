import command_system
import vk_utils


def help(player_id, command_text):
    command_text = command_text.lstrip()
    if command_text:
        if command_text[0] not in ('/', '!'):
            command_text = '/' + command_text
        try:
            command = command_system.get_command(command_text)
        except ValueError:
            return ['Указанная команда не найдена.']
        message = command_text + command.description
        return [message]

    groups = [
        ['гайд', 'помощь', 'правила'],
        ['игрок', 'ник', 'сменить_ник', 'топ', 'рейтинг', 'шанс'],
        ['игра', 'открыть', 'войти', 'начать', 'победа', 'отмена_победы', 'изменить_описание', 'переименовать', 'выйти', 'кикнуть', 'удалить'],
        ['игры', 'все', 'текущие', 'завершённые'],
        ['спать', 'выбор_племени']
    ]

    commands_shown = []

    message = 'Список команд:\n\n'
    for group in groups:
        message += '* * *\n\n'
        for cmd_name in group:
            c = command_system.user_commands.get_command(cmd_name)
            message += '/' + c.keys[0] + c.description + '\n\n'
            commands_shown.append(c)

    first = True
    for c in command_system.get_user_command_list():
        if c not in commands_shown:
            if first:
                message += '* * *\n\n'
                first = False
            message += '/' + c.keys[0] + c.description + '\n\n'

    message = vk_utils.protect_empty_lines(message)
    return [message]


help_command = command_system.UserCommand()

help_command.keys = ['помощь', 'команды', 'help', 'commands']
help_command.description = ' [название_команды] - описание указанной команды, или всех команд.'
help_command.process = help
