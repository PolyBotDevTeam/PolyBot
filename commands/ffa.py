import command_system
import polybot_responses as responses
import utils


_TAGS_FOR_SHOWING_GAME_INFO = ('game', 'игра', 'info', 'инфо')
_TAGS_FOR_SHOWING_OPEN_GAMES = ('', 'open_list', 'список_открытых', 'открытые')
_TAGS_FOR_OPENING_GAME = ('open', 'create', 'открыть', 'создать')
_TAGS_FOR_JOINING_GAME = ('join', 'войти', 'зайти')
_TAGS_FOR_STARTING_GAME = ('start', 'начать')
_TAGS_FOR_FINISHING_GAME = ('finish', 'завершить')


def _can_convert_to_int(string):
    try:
        int(string)
    except ValueError:
        result = False
    else:
        result = True
    return result


def _process_ffa_command(actor, command_text, **kwargs):
    try:
        prefix, command_text = utils.split_one(command_text)
    except ValueError:
        prefix = ''

    if _can_convert_to_int(prefix):
        first_arg = prefix
        try:
            prefix, command_text = utils.split_one(command_text)
        except ValueError:
            prefix = _TAGS_FOR_SHOWING_GAME_INFO[0]
        command_text = f'{first_arg} {command_text}'

    tag = prefix

    if tag in _TAGS_FOR_SHOWING_GAME_INFO:
        command_name = '/ffa_game'
    elif tag in _TAGS_FOR_SHOWING_OPEN_GAMES:
        command_name = '!show_ffa_list'
    elif tag in _TAGS_FOR_OPENING_GAME:
        command_name = '/open_ffa'
    elif tag in _TAGS_FOR_JOINING_GAME:
        command_name = '/join_ffa'
    elif tag in _TAGS_FOR_STARTING_GAME:
        command_name = '/start_ffa'
    elif tag in _TAGS_FOR_FINISHING_GAME:
        command_name = '/finish_ffa'
    else:
        return [responses.UNKNOWN_FFA_COMMAND_TAG]

    command = command_system.get_command(command_name)
    return command(actor, command_text, **kwargs)


description = (
    'Общая команда для управления ФФА-играми. '
    'Вызов без аргументов покажет открытые ФФА. '
    'Вызов с числом покажет информацию об ФФА с данным айди. '
    'Также можно вызывать с ключевыми словами, например /ффа открыть описание, '
    'или /ффа войти айди_игры, точно так же можно начать/завершить ФФА.'
)


ffa_command = command_system.Command(
    process=_process_ffa_command,
    keys=['ффа', 'игры_ффа', 'ffa', 'games_ffa', 'ffa_games'],
    description=description,
    signature='[айди_игры] [ключевое_слово] [аргументы]',
    allow_users=True
)
