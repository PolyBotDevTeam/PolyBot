import command_system
import elo
from message_handler import username
import message_handler
import utils
import vk_utils


def game(player_id, command_text):
    try:
        game_id, command_text = utils.split_one(command_text)
        del command_text
        game_id = int(game_id)
    except ValueError:
        message = 'Необходимо ввести ID игры.'
        return [message]

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT type, is_rated, host_id, away_id, description, time_updated, host_winner, name FROM games WHERE game_id = %s;', (game_id, ))
        fetch = cur.fetchone()
        if not fetch:
            message = 'Не найдено игр с указанным ID.'
            return [message]
        game_type, is_rated, host_id, away_id, description, time_updated, host_winner, name = fetch
        del fetch

        if description is not None:
            description = vk_utils.break_mentions(description)
        if name is not None:
            name = vk_utils.break_mentions(name)

        host_username = username(host_id)
        away_username = username(away_id) if away_id is not None else None
        if host_winner is not None:
            winner_id = host_id if host_winner else away_id
        else:
            winner_id = None
        winner_username = username(winner_id) if winner_id is not None else None

        is_rated_info = '' if is_rated else ' (нерейтинговая)'

        if game_type == 'o':
            message = f'Игра №{game_id}{is_rated_info}.\nХост: {host_username}\nОписание: {description}\nИгра открыта, к ней можно присоединиться командой /войти {game_id}'
        elif game_type == 'r':
            host_mention = vk_utils.create_mention(host_id, host_username)
            message = f'Игра №{game_id}{is_rated_info}.\n{host_username} vs {away_username}\nОписание: {description}\nИгра ждёт своего начала. {host_mention}, начните игру.'
        else:
            message = f'Игра №{game_id} - {name}{is_rated_info}.\n{host_username} vs {away_username}\nОписание: {description}\n'

        if game_type == 'c':
            message += 'Победитель: %s\n' % winner_username
            deltas = elo.fetch_rating_deltas(game_id, cur)
            changes_desc = "%s: %s\n%s: %s" % (
                username(host_id), _get_change_desc(*deltas[0]),
                username(away_id), _get_change_desc(*deltas[1])
            )
            return [message, changes_desc]
        elif game_type == 'i':
            message += 'Игра в процессе.'
        elif game_type == 'w':
            if host_winner:
                message += '{1} объявлен победителем. [id{3}|{2}], подтвердите победу противника командой /победил противник {0}'.format(game_id, host_username, away_username, away_id)
            else:
                message += '{2} объявлен победителем. [id{3}|{1}], подтвердите победу противника командой /победил противник {0}'.format(game_id, host_username, away_username, host_id)

        return [message]


def _get_change_desc(old_rating, new_rating):
    delta = round(new_rating - old_rating)
    old_rating = round(old_rating)
    new_rating = round(new_rating)
    if delta > 0:
        sign = '+'
    elif delta == 0:
        sign = ''
    else:
        sign = '-'
    delta_abs = abs(delta)
    return "%s -> %s (%s%s)" % (old_rating, new_rating, sign, delta_abs)


game_command = command_system.UserCommand()

game_command.keys = ['игра', 'game']
game_command.description = ' ID_игры - Посмотреть информацию об игре.'
game_command.process = game
