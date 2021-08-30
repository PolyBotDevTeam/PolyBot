import command_system


def open_ffa(actor, description, *, database):
    ffa_games = database.ffa_games
    try:
        game = ffa_games.create_game(actor, description)
    except ffa_games.FFAGame.errors.EmptyDescriptionError:
        return ['Описание игры не может быть пустым. Оно указывается после имени команды через пробел.']
    except ffa_games.FFAGame.errors.DescriptionTooLongError:
        return ['Описание игры слишком длинное. Чтобы открыть игру, вам нужно сделать его короче.']
    except ffa_games.FFAGame.errors.InvalidDescriptionError:
        raise
    text = f'Игра {game.id} успешно создана!'
    return [text]


def _open_ffa_process(actor, command_text, *, database, **kwargs):
    return open_ffa(actor, description=command_text, database=database)


open_ffa_command = command_system.Command(
    process=_open_ffa_process,
    keys=['открыть_ффа', 'открытьффа', 'создать_ффа', 'создатьффа', 'open_ffa', 'openffa'],
    description='Открыть новую ффа-игру в боте',
    signature='описание',
    allow_users=False
)
