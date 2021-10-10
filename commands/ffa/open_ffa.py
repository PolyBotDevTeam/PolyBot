import command_system
import polybot_responses as responses


def open_ffa(actor, description, *, is_rated, database):
    ffa_games = database.ffa_games
    errors = ffa_games.FFAGame.errors

    try:
        game = ffa_games.create_game(actor, description, is_rated=is_rated)
    except errors.EmptyDescriptionError:
        return [responses.EMPTY_DESCRIPTION_ERROR]
    except errors.DescriptionTooLongError:
        return [responses.DESCRIPTION_TOO_LONG_ERROR]
    except errors.InvalidDescriptionError:
        raise

    message_about_opened_game = responses.FFA_GAME_OPENED.format(
        game_id=game.id,
        description=game.description
    )

    return [message_about_opened_game]


def _process_open_ffa_command(actor, command_text, *, database, **kwargs):
    return open_ffa(actor, description=command_text, is_rated=True, database=database)


open_ffa_command = command_system.Command(
    process=_process_open_ffa_command,
    keys=['открыть_ффа', 'открытьффа', 'создать_ффа', 'создатьффа', 'open_ffa', 'openffa'],
    description='Открыть рейтинговую ФФА-игру в боте',
    signature='описание',
    allow_users=True
)


def _process_open_unrated_ffa_command(actor, command_text, *, database, **kwargs):
    return open_ffa(actor, description=command_text, is_rated=False, database=database)


open_unrated_ffa_command = command_system.Command(
    process=_process_open_unrated_ffa_command,
    keys=[
        'открыть_нерейтинговую_ффа', 'открыть_анрейт_ффа' 'открытьанрейтффа',
        'open_unrated_ffa', 'openunratedffa'
    ],
    description='Открыть нерейтинговую ФФА-игру в боте',
    signature='описание',
    allow_users=True
)
