import command_system
import message_handler
import elo
import vk_utils
from db_utils import select


def chance(player_id, command_text):
    try:
        host, away = command_text.split()
    except ValueError:
        return ['Должно быть ровно два аргумента.', 'Напишите /помощь шанс, чтобы узнать, как пользоваться командой.']

    elo.recalculate()

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()

        try:
            host = message_handler.try_to_identify_id(host, cur)
            away = message_handler.try_to_identify_id(away, cur)
        except vk_utils.InvalidMentionError:
            message = 'Некорректная ссылка. Нажмите @ или * чтобы выбрать среди участников беседы.'
            return [message]
        except ValueError:
            message = 'Какой-то из указанных никнеймов не найден в системе.'
            return [message]

        try:
            ((host_elo,),) = select(cur, 'SELECT host_elo FROM players WHERE player_id = %s;', host)
            ((away_elo,),) = select(cur, 'SELECT elo FROM players WHERE player_id = %s;', away)
        except ValueError:
            return ['Кто-то из указанных пользователей ещё не зарегистрирован в системе.']

        host_chance, away_chance = elo.calculate_expected_scores(host_elo, away_elo)
        host_percentage = round(host_chance * 100)
        away_percentage = 100 - host_percentage
        message = f'Ожидаемый шанс победы хоста: {host_percentage}%\nОжидаемый шанс победы второго: {away_percentage}%'
        return [message]


command = command_system.UserCommand()

command.keys = ['шанс', 'chance']
command.description = ' хост второй (нужны никнеймы игроков или ссылки на их профили в формате @ссылка) - Ожидаемые шансы победы на основе рейтинга.'
command.process = chance
