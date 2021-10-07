import command_system
import polybot_responses as responses
import vk_utils


_OPEN_MODE_KEYS = ('', 'open')


def ffa_games(command_mode_key, *, database, vk):
    ffa_games = database.ffa_games

    if command_mode_key in _OPEN_MODE_KEYS:
        games = ffa_games.get_open_games()
        game_template = responses.OPEN_FFA_GAMES_ITEM
        whole_message_template = responses.OPEN_FFA_GAMES
    else:
        raise ValueError('invalid command mode:', command_mode_key)

    games_list = _format_ffa_games(games, game_template)
    result_message_text = whole_message_template.format(games_list=games_list)

    return [result_message_text]


def _format_ffa_games(games, game_template, *, separator='\n\n'):
    texts_about_games = []

    for game in games:
        owner_username = vk_utils.fetch_username(game.owner_id, vk=vk)
        if game.is_finished():
            winner_username = vk_utils.fetch_username(game.winner_id, vk=vk)
        else:
            winner_username = None
        formatting_kwargs = {
            'game_id': game.id,
            'owner_username': owner_username,
            'description': game.description,
            'game_name': game.name if game.is_started() else None,
            'winner_username': winner_username
        }
        text_about_game = game_template.format(**formatting_kwargs)
        texts_about_games.append(text_about_game)

    return separator.join(texts_about_games)


def _process_ffa_games_command(actor, command_text, *, database, vk, **kwargs):
    return ffa_games(command_text.rstrip(), database=database, vk=vk)


_description = (
    'Просмотреть список ФФА. '
    'По-умолчанию отображаются ФФА, к которым можно присоединиться.'
)


ffa_games_command = command_system.Command(
    process=_process_ffa_games_command,
    keys=['show_ffa_list'],
    description=_description,
    signature='[стадия]',
    allow_users=False
)
