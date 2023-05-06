import command_system
import elo
import vk_utils


guide_after_registration = """
Основные комманды бота:
1. </открытые> - просмотреть список игр, к которым можно присоединиться.
2. </войти айди_игры> - присоединиться к открытой игре.
3. </победил я/противник айди_игры> - объявить результат игры.

Если вы хотите открыть свою игру, понадобятся следующие команды:
1. </открыть описание> - создать игру в боте. Другие игроки смогут вступить в неё.
2. </начать айди_игры название_игры_в_политопии> - объявить о старте игры с противником.

Не забывайте, что у игр в боте есть </правила>.
Полный список команд можно просмотреть командой </команды>.
Чтобы получить помощь по какой-либо команде, напишите </помощь имя_команды>.
"""
guide_after_registration = guide_after_registration.strip()

guide_after_registration = vk_utils.highlight_marked_text_areas(guide_after_registration)


def _process_registration_command(player_id, command_text, *, database, **kwargs):
    args = command_text.split()
    if not args:
        message = 'Необходимо ввести свой никнейм. Его можно найти в Throne Room, а также во вкладках Friends и Profile. Вводите данные через пробел в формате /ник ваш_никнейм'
        return [message]
    nickname = ' '.join(args)

    if not 1 <= len(nickname) <= 32:
        message = 'Недопустимая длина никнейма. Убедитесь что указан ваш никнейм. Его можно найти в Throne Room, а также во вкладке Profile.'
        return [message]

    connection = database.create_connection()
    with connection:
        cursor = connection.cursor()

        if _is_nickname_already_taken(nickname, cursor=cursor):
            if player_id == _get_nickname_owner(nickname, cursor=cursor):
                response = ['Вы уже зарегистрировались с данным никнеймом.']
            else:
                message = 'Этот никнейм уже занят.'
                hint = 'Если это ваш никнейм, обратитесь к администратору.'
                response = [message, hint]

        elif _is_player_already_registered(player_id, cursor=cursor):
            _update_nickname(player_id, nickname, cursor=cursor)
            message = f'Никнейм успешно обновлён.\nВаш новый никнейм: {nickname}'
            response = [message]

        else:
            _register_new_player(player_id, nickname, database=database, cursor=cursor)
            players_banned = _count_players_banned(cursor=cursor)
            message = f'Вы успешно зарегистрированы в системе!\nВаш никнейм: {nickname}\n\nИграйте честно!\nЧитеров уже забанено: {players_banned}'
            response = [message, guide_after_registration]

    return response


def _is_nickname_already_taken(nickname, *, cursor):
    cursor.execute('SELECT EXISTS(SELECT * FROM players WHERE nickname = %s);', nickname)
    [[result]] = cursor
    return result


def _get_nickname_owner(nickname, *, cursor):
    cursor.execute('SELECT player_id FROM players WHERE nickname = %s;', nickname)
    [[result]] = cursor
    return result


def _is_player_already_registered(player_id, *, cursor):
    cursor.execute('SELECT EXISTS(SELECT player_id FROM players WHERE player_id = %s);', player_id)
    [[result]] = cursor
    return result


def _update_nickname(player_id, new_nickname, *, cursor):
    cursor.execute('UPDATE players SET nickname = %s WHERE player_id = %s;', (new_nickname, player_id))


def _register_new_player(player_id, nickname, *, database, cursor):
    cursor.execute(
        'INSERT players(player_id, nickname, host_elo, away_elo, joining_time, banned) VALUES (%s, %s, %s, %s, NOW(), %s);',
        (player_id, nickname, elo.DEFAULT_ELO.host, elo.DEFAULT_ELO.away, False)
    )
    elo.recalculate(database=database)


def _count_players_banned(*, cursor):
    cursor.execute('SELECT COUNT(*) FROM players WHERE banned = 1;')
    [[result]] = cursor
    return result


registration_command = command_system.Command(
    process=_process_registration_command,
    keys=[
        'сменить_ник', 'сменить_никнейм', 'изменить_ник', 'изменить_никнейм', 'регистрация',
        'change_nick', 'change_nickname', 'registration'
    ],
    description='Регистрация/обновление ника в боте посредством ввода своего никнейма',
    signature='никнейм',
    allow_users=True
)
