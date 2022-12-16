import command_system
from elo import DEFAULT_ELO
import message_handler
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


def set_nickname(player_id, command_text):
    args = command_text.split()
    if not args:
        message = 'Необходимо ввести свой никнейм. Его можно найти в Throne Room, а также во вкладках Friends и Profile. Вводите данные через пробел в формате /ник ваш_никнейм'
        return [message]
    nickname = ' '.join(args)

    if not 1 <= len(nickname) <= 32:
        message = 'Недопустимая длина никнейма. Убедитесь что указан ваш никнейм. Его можно найти в Throne Room, а также во вкладке Profile.'
        return [message]

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()

        cur.execute('SELECT EXISTS(SELECT * FROM players WHERE nickname = %s);', nickname)
        [[is_already_taken]] = cur
        if is_already_taken:
            cur.execute('SELECT player_id FROM players WHERE nickname = %s;', nickname)
            [[nickname_owner]] = cur
            if player_id == nickname_owner:
                response = ['Вы уже зарегистрировались с данным никнеймом.']
            else:
                message = 'Этот никнейм уже занят.'
                hint = 'Если это ваш никнейм, обратитесь к администратору.'
                response = [message, hint]
            return response

        cur.execute('SELECT EXISTS(SELECT player_id FROM players WHERE player_id = %s);', player_id)
        if cur.fetchone()[0]:
            cur.execute('UPDATE players SET nickname = %s WHERE player_id = %s;', (nickname, player_id))
            message = 'Никнейм успешно обновлён.\nВаш новый никнейм: {}'.format(nickname)
            return [message]
        else:
            cur.execute(
                'INSERT players(player_id, nickname, host_elo, away_elo, joining_time, banned) VALUES (%s, %s, %s, %s, NOW(), %s);',
                (player_id, nickname, DEFAULT_ELO.host, DEFAULT_ELO.away, False)
            )
            cur.execute('SELECT COUNT(*) FROM players WHERE banned = 1;')
            message = 'Вы успешно зарегистрированы в системе!\nВаш никнейм: {}\n\nИграйте честно!\nЧитеров уже забанено: {}'.format(nickname, cur.fetchone()[0])
            return [message, guide_after_registration]


# TODO: вероятно стоит разделить registration и change_nickname на две отдельные команды
registration_command = command_system.UserCommand()

registration_command.keys = ['сменить_ник', 'сменить_никнейм', 'изменить_ник', 'изменить_никнейм', 'регистрация', 'change_nick', 'change_nickname', 'registration']
registration_command.description = ' никнейм - Регистрация/обновление ника в боте посредством ввода своего никнейма.'
registration_command.process = set_nickname
