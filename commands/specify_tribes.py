import json
import os

import command_system
import settings
import utils


def specify_tribes(player_id, command_text):
    try:
        game_id, command_text = utils.split_one(command_text)
        game_id = int(game_id)
    except ValueError:
        return ['Сразу после команды должен идти айди игры.']

    try:
        host, command_text = utils.split_one(command_text)
        away, command_text = utils.split_one(command_text)
        info = command_text
    except ValueError:
        return ['После айди игры должно идти племя хоста и племя второго.']

    data = {
        'author_id': player_id,
        'game_id': game_id,
        'host': host,
        'away': away,
        'info': info
    }

    with open(os.path.join(settings.project_folder, 'tribes_log.txt'), 'a') as fp:
        print(json.dumps(data), file=fp)

    return ['Племена сохранены.']


command = command_system.AdminCommand()  # TODO: UserCommand
command.keys = ['племена', 'указать_племена', 'tribes', 'specify_tribes']
command.description = ' айди_игры племя_хоста племя_второго - указать племена для данной игры для статистики. Можно также указать дополнительную информацию.'
command.process = specify_tribes
