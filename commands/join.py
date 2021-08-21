import command_system
import message_handler


def join(player_id, command_text):
    args = command_text.split()
    if len(args) != 1:
        message = 'Необходимо ввести ID игры в которую вы хотите войти.'
        return [message]
    (game_id,) = args
    game_id = int(game_id)

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT host_id FROM games WHERE game_id = %s AND type = \'o\' AND away_id IS NULL;', (game_id, ))
        fetch = cur.fetchone()
        if not fetch:
            message = 'Не найдено открытых игр с указанным ID.'
            return [message]
        (host_id,) = fetch

        if host_id == player_id:
            message = 'Нельзя играть с самим собой.'
            return [message]

        cur.execute('SELECT nickname FROM players WHERE player_id = %s;', player_id)
        fetch = cur.fetchone()
        if not fetch:
            message = 'Вы не зарегистрированы в системе. Воспользуйтесь справкой: /помощь.'
            return [message]
        (away_nickname,) = fetch
        cur.execute('SELECT nickname FROM players WHERE player_id = %s;', host_id)
        ((host_nickname,),) = cur

        cur.execute('SELECT NOT EXISTS(SELECT * FROM games WHERE host_id = %s AND away_id = %s);', (host_id, player_id))
        ((is_first_game_of_this_pair,),) = cur

        cur.execute('UPDATE games SET away_id = %s, type = \'r\', time_updated = NOW() WHERE game_id = %s;', (player_id, game_id))

        messages_for_away = [f'Вы успешно присоединились к игре {game_id}.']
        if is_first_game_of_this_pair:
            messages_for_away[0] += '\n\n'
            messages_for_away[0] += 'Вам следует добавить своего противника в друзья в Политопии.\n'
            messages_for_away[0] += 'Никнейм вашего противника:'
            messages_for_away.append(host_nickname)

        host_mention = message_handler.create_mention(host_id)
        message_for_host = f'{host_mention}, ваша игра заполнена. Теперь вам нужно создать игру в Политопии. ' \
                           f'Не забудьте применить команду /начать с названием новой игры. Никнейм вашего противника:'
        return [*messages_for_away, message_for_host, away_nickname]


join_command = command_system.UserCommand()

join_command.keys = ['войти', 'зайти', 'join']
join_command.description = ' ID_игры - Войти в открытую игру. Ваш противник создаст игру в Политопии и пригласит вас в неё.'
join_command.process = join
