import command_system
import polybot_responses as responses


def open_ffa(actor, description, *, database):
    ffa_games = database.ffa_games
    errors = ffa_games.FFAGame.errors

    try:
        game = ffa_games.create_game(actor, description)
    except errors.EmptyDescriptionError:
        return [responses.EMPTY_DESCRIPTION_ERROR]
    except errors.DescriptionTooLongError:
        return [responses.DESCRIPTION_TOO_LONG_ERROR]
    except errors.InvalidDescriptionError:
        raise

    return [responses.FFA_GAME_OPENED.format(game=game)]


def _process_open_ffa_command(actor, command_text, *, database, **kwargs):
    return open_ffa(actor, description=command_text, database=database)


open_ffa_command = command_system.Command(
    process=_process_open_ffa_command,
    keys=['открыть_ффа', 'открытьффа', 'создать_ффа', 'создатьффа', 'open_ffa', 'openffa'],
    description='Открыть новую ффа-игру в боте',
    signature='описание',
    allow_users=False
)
