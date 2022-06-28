import command_system
import polybot_responses as responses
import utils


_TAGS_FOR_SHOWING_GAME_INFO = ('game', 'игра', 'info', 'инфо')

_TAGS_FOR_SHOWING_OPEN_GAMES = (
    'games', 'open_list', 'open_games',
    'игры', 'список_открытых', 'открытые_игры', 'открытые'
 )
_TAGS_FOR_SHOWING_INCOMPLETE_GAMES = ('текущие', 'incomplete')
_TAGS_FOR_SHOWING_COMPLETE_GAMES = ('завершённые', 'complete')

_TAGS_FOR_OPENING_GAME = (
    'open', 'open_rated', 'create', 'create_rated',
    'открыть', 'открыть_рейт', 'открыть_рейтинговую',
    'создать', 'создать_рейт', 'создать_рейтинговую'
)
_TAGS_FOR_OPENING_UNRATED_GAME = (
    'open_unrated', 'create_unrated',
    'открыть_анрейт', 'открыть_нерейтинговую',
    'создать_анрейт', 'создать_нерейтинговую'
)
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
        return [_usage_help]

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
        command_name = '/show_ffa_list'
    elif tag in _TAGS_FOR_SHOWING_INCOMPLETE_GAMES:
        command_name = '/show_ffa_list'
        command_text = f'incomplete {command_text}'
    elif tag in _TAGS_FOR_SHOWING_COMPLETE_GAMES:
        command_name = '/show_ffa_list'
        command_text = f'complete {command_text}'

    elif tag in _TAGS_FOR_OPENING_GAME:
        command_name = '/open_ffa'
    elif tag in _TAGS_FOR_OPENING_UNRATED_GAME:
        command_name = '/open_unrated_ffa'
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


_usage_help = '''Варианты использования:
* /ффа айди_игры (информация об указанной ФФА)
* /ффа игры (ФФА, к которым можно присоединиться)
* /ффа текущие
* /ффа завершённые
* /ффа открыть описание
* /ффа открыть_анрейт описание
* /ффа войти айди_игры
* /ффа выйти айди_игры
* /ффа начать айди_игры название_в_политопии
* /ффа завершить айди_игры победитель'''


ffa_command = command_system.Command(
    process=_process_ffa_command,
    keys=['ффа', 'игры_ффа', 'ffa', 'games_ffa', 'ffa_games'],
    description='Общая команда для управления ФФА-играми',
    signature='[айди_игры] [ключевое_слово] [аргументы]',
    allow_users=True
)
