import command_system
import vk_utils


def _process_help_command(player_id, command_text, **kwargs):
    if command_text:
        if command_text[0] not in ('/', '!'):
            command_text = '/' + command_text
        try:
            command = command_system.get_command(command_text)
        except ValueError:
            return ['Указанная команда не найдена.']
        message = command_text + command.description
        return [message]

    sections_by_names = {
        'Информация': [
            'гайд',
            'помощь',
            'правила'
        ],
        'Игроки': [
            'игрок',
            'топ',
            'рейтинг',
            'шанс',
            'ник',
            'сменить_ник'
        ],
        'Просмотр игр': [
            'игра',
            'игры',
            'все',
            'текущие',
            'завершённые'
        ],
        'Управление играми': [
            'открыть',
            'открыть_анрейт',
            'войти',
            'начать',
            'победа',
            'отмена_победы',
            'изменить_описание',
            'переименовать',
            'выйти',
            'кикнуть',
            'удалить'
        ],
        'Мудрость': [
            'спать',
            'выбор_племени',
            'ау',
            'зaвёpшeнныe'
        ],
        'ФФА-игры': [
            'ффа'
        ]
    }

    sections_order = ['Общая информация', 'Игроки', 'Просмотр игр', 'Управление играми', 'Мудрость', 'ФФА-игры']

    message = 'Список команд:\n\n'

    for section_name in sections_order:
        section_description = f'* * * {section_name} * * *\n\n'
        for cmd_name in sections_by_names[section_name]:
            section_description += '/' + cmd_name + '\n'
        message += section_description + '\n'

    commands_names_shown = []
    for names_from_section in sections_by_names.values():
        commands_names_shown.extend(names_from_section)

    commands_names_to_ignore = [
        'открыть_ффа', 'открыть_нерейтинговую_ффа',
        'войти_в_ффа', 'начать_ффа', 'завершить_ффа',
        'игра_ффа', 'показать_список_ффа'
    ]

    commands_names_processed = commands_names_shown + commands_names_to_ignore

    user_command_by_name = command_system.user_commands.get_command
    commands_processed = [user_command_by_name(name) for name in commands_names_processed]

    commands_missed = [
        c for c in command_system.get_user_command_list()
        if c not in commands_processed
    ]

    if commands_missed:
        message += '* * *\n\n'
        for c in commands_missed:
            message += '/' + c.keys[0] + c.description + '\n'

    message = vk_utils.protect_empty_lines(message)

    full_description_hint = 'Подробная информация по команде: /помощь имя_команды'

    return [message, full_description_hint]


help_command = command_system.Command(
    process=_process_help_command,
    keys=['помощь', 'команды', 'help', 'commands'],
    description='Описание указанной команды, или всех команд',
    signature='[название_команды]',
    allow_users=True
)
