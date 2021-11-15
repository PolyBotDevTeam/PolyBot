import command_system
import vk_utils


def _process_join_command(player_id, command_text, *, cursor, vk, **kwargs):
    args = command_text.split()
    if len(args) > 1:
        return ['Вы передали слишком много аргументов. Необходимо указать только имя команды и айди игры.']
    elif len(args) == 0:
        return ['Необходимо указать айди игры, в которую вы хотите войти.']
    [game_id] = args

    try:
        game_id = int(game_id)
    except ValueError:
        return ['Вы указали некорректный айди игры, не удалось распознать его как число.']

    cur = cursor
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

    cur.execute(
        'SELECT NOT EXISTS'
        '(SELECT * FROM games WHERE (host_id = %s AND away_id = %s) OR (host_id = %s AND away_id = %s));',
        (host_id, player_id, player_id, host_id)
    )
    ((is_first_game_of_this_pair,),) = cur

    cur.execute('UPDATE games SET away_id = %s, type = \'r\', time_updated = NOW() WHERE game_id = %s;', (player_id, game_id))

    messages_for_away = [f'Вы успешно присоединились к игре {game_id}.']
    if is_first_game_of_this_pair:
        messages_for_away[0] += '\n\n'
        messages_for_away[0] += 'Вам следует добавить своего противника в друзья в Политопии.'
    messages_for_away[0] += '\n'
    messages_for_away[0] += 'Никнейм вашего противника:'
    messages_for_away.append(host_nickname)

    host_mention = vk_utils.create_mention(host_id, vk=vk)
    message_for_host = f'{host_mention}, ваша игра заполнена. Теперь вам нужно создать игру в Политопии. ' \
                       f'Не забудьте применить команду /начать с названием новой игры. Никнейм вашего противника:'
    return [*messages_for_away, message_for_host, away_nickname]


join_command = command_system.Command(
    process=_process_join_command,
    keys=['войти', 'зайти', 'join'],
    description='Войти в открытую игру. Ваш противник создаст игру в Политопии и пригласит вас в неё',
    signature='айди_игры',
    allow_users=True
)
