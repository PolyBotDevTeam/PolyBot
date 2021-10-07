import itertools

import command_system
import message_handler
from message_handler import username
import utils


def complete(actor_id, command_text):
    try:
        page, pointer = utils.split_one(command_text)
        page = int(page)
    except ValueError:
        pointer = command_text
        page = 1

    pointer = pointer if pointer else None

    connection = message_handler.create_connection()
    with connection:
        cur = connection.cursor()
        self = pointer is None
        if self:
            target_player_id = actor_id
        else:
            try:
                target_player_id = message_handler.try_to_identify_id(pointer, cur)
            except ValueError:
                message = 'Некорректная ссылка или никнейм. Нажмите @ или * чтобы выбрать среди участников беседы.'
                return [message]

        message = 'Завершённые игры с вашим участием (страница %s):\n\n' if self else 'Завершённые игры с участием игрока (страница %s):\n\n'
        message %= page
        cur.execute('SELECT game_id, name, host_id, away_id, description, host_winner FROM games WHERE type = \'c\' AND (host_id = %s OR away_id = %s) ORDER BY time_updated DESC;', (target_player_id, target_player_id))
        count = 0
        for game_id, name, host_id, away_id, description, host_winner in cur:
            if count // 10 + 1 == page:
                result = 'ПОБЕДА' if host_winner == (target_player_id == host_id) else 'ПОРАЖЕНИЕ'
                message += f'{game_id} - {name}\n{username(host_id)} vs {username(away_id)}\n{description}\n{result}\n\n'
            count += 1

        messages = [message]
        if page == 1:
            hint_about_next_page = f'Для просмотра следующей страницы напишите /завершённые {page+1}'
            if pointer is not None:
                # TODO: maybe should use nicknames instead
                hint_about_next_page += f' {username(target_player_id)}'
                # hint_about_next_page += f' {pointer}'
            messages.append(hint_about_next_page)
        return messages


complete_command = command_system.UserCommand()

keys = ['завершённые', 'завершенные', 'complete']
pattern = 'з_вё_ш_нны_'.replace('_', '%s')
for fillers in itertools.product('аa', 'рp', 'еe', 'еe'):
    keys.append(pattern % fillers)
keys.remove('завёршенные')

complete_command.keys = keys
complete_command.description = ' номер страницы игр (по 10 на странице) [упоминание игрока] - Завершённые игры.'
complete_command.process = complete
