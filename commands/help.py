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

    get_user_command = command_system.user_commands.get_command

    groups = [
        ['гайд', 'помощь', 'правила'],
        ['игрок', 'ник', 'сменить_ник', 'топ', 'рейтинг', 'шанс'],
        ['игра', 'открыть', 'войти', 'начать', 'победа', 'отмена_победы', 'изменить_описание', 'переименовать', 'выйти', 'кикнуть', 'удалить'],
        ['игры', 'все', 'текущие', 'завершённые'],
        ['спать', 'выбор_племени'],
        ['ффа']
    ]

    commands_to_ignore = [
        'открыть_ффа', 'открыть_нерейтинговую_ффа',
        'войти_в_ффа', 'начать_ффа', 'завершить_ффа',
        'игра_ффа', 'показать_список_ффа'
    ]
    commands_to_ignore = [get_user_command(name) for name in commands_to_ignore]

    commands_shown = []

    message = 'Список команд:\n\n'
    for group in groups:
        message += '* * *\n\n'
        for cmd_name in group:
            c = get_user_command(cmd_name)
            message += '/' + c.keys[0] + c.description + '\n\n'
            commands_shown.append(c)

    commands_missed = [
        c for c in command_system.get_user_command_list()
        if c not in commands_shown + commands_to_ignore
    ]

    if commands_missed:
        message += '* * *\n\n'
        for c in commands_missed:
            message += '/' + c.keys[0] + c.description + '\n\n'

    message = vk_utils.protect_empty_lines(message)
    return [message]


help_command = command_system.UserCommand()

help_command.keys = ['помощь', 'команды', 'help', 'commands']
help_command.description = ' [название_команды] - описание указанной команды, или всех команд.'
help_command.process = help
