import command_system
import polybot_responses as responses


def join_ffa(actor, game_id, *, database):
    ffa_games = database.ffa_games
    try:
        game = ffa_games.get_game_by_id(game_id)
    except ffa_games.errors.GameNotFoundError:
        return [responses.GAME_NOT_FOUND_ERROR]

    # If the game is already started and the actor has already joined,
    # then the second fact is more important to tell about.
    # So should check it before exceptions processing.
    if game.has_member(actor):
        return [responses.ALREADY_JOINED_ERROR]

    try:
        game.add_member(actor)
    except game.errors.AlreadyStartedError:
        return [responses.UNABLE_TO_JOIN_STARTED_ERROR]
    except game.errors.AlreadyMemberError:
        raise

    return [responses.JOINED_FFA_GAME.format(game_id=game.id)]


def _process_join_ffa_command(actor, command_text, *, database, **kwargs):
    if not database.players.is_registered(actor):
        return [responses.NOT_REGISTERED_ERROR]

    if not command_text:
        return [responses.MISSING_ID_ERROR]
    try:
        game_id = int(command_text)
    except ValueError:
        return [responses.INVALID_ID_SYNTAX_ERROR]

    return join_ffa(actor, game_id, database=database)


join_ffa_command = command_system.Command(
    process=_process_join_ffa_command,
    keys=[
        'войти_в_ффа', 'войтивффа',
        'войти_ффа', 'войтиффа',
        'зайти_в_ффа', 'зайтивффа',
        'зайти_ффа', 'зайтиффа',
        'join_ffa', 'joinffa'
    ],
    description='Присоединиться к ффа-игре',
    signature='айди_игры',
    allow_users=True
)
