import command_system
import polybot_responses as responses
import utils


def start_ffa(actor, game_id, game_name, *, database):
    ffa_games = database.ffa_games
    try:
        game = ffa_games.get_game_by_id(game_id)
    except ffa_games.errors.GameNotFoundError:
        return [responses.GAME_NOT_FOUND_ERROR]

    if not game.is_owner(actor):
        return [responses.NOT_FFA_OWNER_ERROR]

    try:
        game.start(game_name)
    except game.errors.AlreadyStartedError:
        return [responses.ALREADY_STARTED_ERROR]
    except game.errors.InvalidGameNameError:
        if game_name:
            error_message = responses.INVALID_GAME_NAME_ERROR
        else:
            error_message = responses.EMPTY_GAME_NAME_ERROR
        return [error_message]

    return [responses.FFA_GAME_STARTED.format(game_id=game.id)]


def _process_start_ffa_command(actor, command_text, *, database, **kwargs):
    if not command_text:
        return [responses.START_FFA_NO_ARGUMENTS_ERROR]

    game_id, game_name = utils.split_one(command_text)

    try:
        game_id = int(game_id)
    except ValueError:
        return [responses.INVALID_ID_SYNTAX_ERROR]

    return start_ffa(actor, game_id, game_name, database=database)


start_ffa_command = command_system.Command(
    process=_process_start_ffa_command,
    keys=['начать_ффа', 'начатьффа', 'start_ffa', 'startffa'],
    description='Начать ффа-игру',
    signature='айди_игры название_игры',
    allow_users=True
)
