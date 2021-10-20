NOT_REGISTERED_ERROR = (
    'Для использования этой команды необходимо зарегистрироваться в боте. '
    'Это можно сделать командой /регистрация ваш_никнейм_в_политопии'
)
UNABLE_TO_IDENTIFY_USER = 'Не удалось обнаружить пользователя по введённым данным.'

EMPTY_DESCRIPTION_ERROR = 'Описание игры не может быть пустым. Оно указывается в конце команды.'
DESCRIPTION_TOO_LONG_ERROR = 'Описание игры слишком длинное. Чтобы открыть игру, вам нужно сделать его короче.'
FFA_GAME_OPENED = '''Игра {game_id} создана!
Описание: {description}'''

GAME_NOT_FOUND_ERROR = 'Не удалось найти игру с таким айди.'

UNABLE_TO_JOIN_STARTED_ERROR = 'Нельзя присоединиться к уже начатой игре.'
ALREADY_JOINED_ERROR = 'Вы уже вступили в эту игру.'
JOINED_FFA_GAME = 'Вы присоединились к игре {game_id}.'

MISSING_ID_ERROR = 'После имени команды необходимо указать айди игры через пробел.'
INVALID_ID_SYNTAX_ERROR = 'Вы указали некорректный айди, не удалось распознать его как число.'


START_FFA_NO_ARGUMENTS_ERROR = (
    'После имени команды необходимо указать айди игры через пробел, '
    'а в конце команды название вашей игры в политопии.'
)
NOT_FFA_OWNER_ERROR = 'Вы не являетесь создателем данной игры.'
INVALID_GAME_NAME_ERROR = 'Пожалуйста, введите именно то название игры, которое указано в Политопии.'
EMPTY_GAME_NAME_ERROR = 'В конец команды нужно добавить название игры, указанное в Политопии.'
ALREADY_STARTED_ERROR = 'Данная игра уже начата.'
FFA_GAME_STARTED = '''Игра {game_id} начата!
Название игры: {name}
Участники:
{members_mentions}'''

FINISH_FFA_NO_ARGUMENTS_ERROR = (
    'После имени команды необходимо указать айди игры через пробел, '
    'а в конце команды победителя данной игры (нужны имя и фамилия, либо упоминание)'
)
WINNER_IS_NOT_SPECIFIED_ERROR = 'Вы забыли указать победителя в конце команды (нужны имя и фамилия, либо упоминание)'
WINNER_IS_NOT_A_MEMBER_ERROR = 'Указанный победитель не является участником данной игры.'
UNABLE_TO_FINISH_UNSTARTED_GAME = 'Данная игра ещё не начата.'
ALREADY_FINISHED_ERROR = 'Данная игра уже завершена.'
FFA_GAME_FINISHED = 'ФФА {game_id} завершена, победитель - {winner_mention}!'


OPEN_FFA_GAMES = '''Открытые ФФА:

{games_list}'''
OPEN_FFA_GAMES_ITEM = '''ID: {game_id} - {owner_username}
Описание: {description}'''

INCOMPLETE_FFA_GAMES = '''Текущие ФФА:

{games_list}'''
INCOMPLETE_FFA_GAMES_ITEM = '''ID: {game_id} - {game_name}
Создатель: {owner_username}
Описание: {description}'''


GAME_IS_RATED = 'Рейтинговая'
GAME_IS_UNRATED = 'Нерейтинговая'

OPEN_FFA_GAME_INFO = '''ФФА №{game_id} - Открыта.
Создатель: {owner_username}
Тип: {is_rated_info}
Описание: {description}
Участники:
{members_usernames}'''

STARTED_FFA_GAME_INFO = '''ФФА №{game_id} - Идёт.
Создатель: {owner_username}
Тип: {is_rated_info}
Описание: {description}
Название: {name}
Участники:
{members_usernames}'''

FINISHED_FFA_GAME_INFO = '''ФФА №{game_id} - Завершена.
Создатель: {owner_username}
Тип: {is_rated_info}
Описание: {description}
Название: {name}
Победитель: {winner_username}
Участники:
{members_usernames}'''


UNKNOWN_FFA_COMMAND_TAG = 'Не удалось определить, какое действие вы хотите совершить. Воспользуйтесь командой /помощь ффа'
