import command_system
import elo
import message_handler
from message_handler import username, create_mention
from db_utils import select
import polybot_utils


me = ('я', 'me')
opponent = ('противник', 'соперник', 'враг', 'оппонент', 'opponent', 'enemy')


def win(player_id, command_text):
    args = command_text.split()
    try:
        winner, game_id = args
        game_id = int(game_id)
        if winner not in me and winner not in opponent:
            message = 'Необходимо указать победителя (я/противник).'
            return [message]
    except:
        message = 'Необходимо указать победителя (я/противник) и ID игры в системе.'
        return [message]

    winner_is_me = winner in me

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()

        cur.execute('SELECT host_id, away_id, type FROM games WHERE game_id = %s;', game_id)
        fetch = cur.fetchone()
        if fetch is None:
            return ['Не найдено игр с указанным ID.', 'Напишите /текущие, чтобы посмотреть список игр с вашим участием.']
        host_id, away_id, game_type = fetch
        del fetch

        if player_id not in (host_id, away_id):
            return ['Вы не участвуете в данной игре.', 'Напишите /текущие, чтобы посмотреть список игр с вашим участием.']

        if game_type not in ('i', 'w'):
            if game_type == 'o':
                message = 'Игра ещё не заполнена.'
                hint = 'Скорее всего вы указали неправильный айди игры.\nНапишите /текущие, чтобы посмотреть список игр с вашим участием.'
            elif game_type == 'r':
                message = 'Сначала необходимо начать игру.'
                hint = 'Напишите /начать %s название_игры_в_политопии' % game_id
            elif game_type == 'c':
                message = 'Результат игры уже нельзя изменить.'
                hint = 'Если вы считаете, что что-то пошло не так, обратитесь к администратору.'
            else:
                raise RuntimeError('unsupported game type: %s' % game_type)
            return [message, hint]

        host_winner = (winner_is_me and player_id == host_id) or (not winner_is_me and player_id == away_id)
        host_winner = int(host_winner)
        winner_id = host_id if host_winner else away_id
        loser_id = away_id if host_winner else host_id

        new_game_type = 'w' if winner_is_me else 'c'
        cur.execute('UPDATE games SET host_winner = %s, type = %s, time_updated = NOW() WHERE game_id = %s;', (host_winner, new_game_type, game_id))
        message = f'Игра {game_id} завершена, победитель - {username(winner_id)}!'
        result = [message]

        if winner_is_me:
            notification = f'{create_mention(loser_id)}, подтвердите победу вашего противника командой /победил противник {game_id}. Если вы не согласны с его заявлением, обратитесь к модератору.'
            result.append(notification)
        else:
            polybot_utils.process_game_finish(game_id, cursor=cur)
            elo.recalculate(cur=cur)
            deltas = elo.fetch_rating_deltas(game_id, cur)
            changes_desc = "%s: %s\n%s: %s" % (
                username(host_id), _get_change_desc(*deltas[0]),
                username(away_id), _get_change_desc(*deltas[1])
            )
            result.append(changes_desc)

        return result


def _select_engaged_elo(host_id, away_id, cur):
    ((host_elo,),) = select(cur, 'SELECT host_elo FROM players WHERE player_id = %s;', host_id)
    ((away_elo,),) = select(cur, 'SELECT elo FROM players WHERE player_id = %s;', away_id)
    return elo.ELO(host_elo, away_elo)


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


win_command = command_system.UserCommand()

win_command.keys = ['победа', 'победил', 'win']
win_command.description = ' я/противник ID_игры - Объявить о победе в игре. При сообщении о своей победе придётся дождаться подтверждения противника или подождать сутки.'
win_command.process = win
