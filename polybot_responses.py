NOT_REGISTERED_ERROR = (
    'Для этой команды необходимо зарегистрироваться в боте. '
    'Сделать это можно командой /регистрация ваш_никнейм_в_политопии'
)

EMPTY_DESCRIPTION_ERROR = 'Описание игры не может быть пустым. Оно указывается после имени команды через пробел.'
DESCRIPTION_TOO_LONG_ERROR = 'Описание игры слишком длинное. Чтобы открыть игру, вам нужно сделать его короче.'
FFA_GAME_OPENED = 'Игра {game_id} успешно создана!'

GAME_NOT_FOUND_ERROR = 'Не удалось найти игру с таким айди.'

ALREADY_JOINED_ERROR = 'Вы уже вступили в эту игру.'
JOINED_FFA_GAME = 'Вы успешно присоединились к игре {game_id}.'

MISSING_ID_ERROR = 'После имени команды необходимо указать айди игры через пробел.'
INVALID_ID_SYNTAX_ERROR = 'Вы указали некорректный айди, не удалось распознать его как число.'

START_FFA_NO_ARGUMENTS_ERROR = (
    'После имени команды необходимо указать айди игры через пробел, '
    'а после него название вашей игры в политопии.'
)
NOT_FFA_OWNER_ERROR = 'Вы не являетесь создателем данной игры.'
INVALID_GAME_NAME_ERROR = 'Пожалуйста, введите именно то название игры, которое указано в Политопии.'
EMPTY_GAME_NAME_ERROR = 'Вы забыли ввести название игры, указанное в Политопии.'
ALREADY_STARTED_ERROR = 'Данная игра уже была начата.'
FFA_GAME_STARTED = 'Игра {game_id} успешно начата!'

OPEN_FFA_GAMES_HEADER = 'Открытые ффа-игры:'
OPEN_FFA_GAMES_ITEM = '''ID: {game_id} - {owner_username}
{description}'''

OPEN_FFA_GAME_INFO = '''ФФА №{game_id}.
Создатель: {owner_username}
Описание: {description}
Участники:
{members_usernames}'''

STARTED_FFA_GAME_INFO = '''ФФА №{game_id}.
Создатель: {owner_username}
Описание: {description}
Название: {name}
Участники:
{members_usernames}'''

FINISHED_FFA_GAME_INFO = '''ФФА №{game_id}.
Создатель: {owner_username}
Описание: {description}
Название: {name}
Победитель: {winner_username}
Участники:
{members_usernames}'''
