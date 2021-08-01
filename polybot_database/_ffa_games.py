import polybot_database._ffa_game as _ffa_game_module


# TODO: Rename this class
class FFAGames:

    def __init__(self, *, execute_query):
        self._execute = execute_query
        self._errors = _FFAGamesErrors()

    @property
    def errors(self):
        return self._errors

    def get_game_by_id(self, game_id):
        game = _ffa_game_module.FFAGame(game_id=game_id, execute_query=self._execute)
        if not game.exists():
            raise self.errors.GameNotFoundError('the game with this id does not exist')
        return game

    def create_game(self, owner_id, description):
        [[game_id]] = self._execute(
            'INSERT ffa_games(owner_id, description) VALUES (%s, %s);\n'
            'SELECT LAST_INSERT_ID();',
            [owner_id, description]
        )
        return self.get_game_by_id(game_id)

    def get_games_of_player(self, player_id):
        raise NotImplementedError


class _FFAGamesErrors:

    def __init__(self):
        pass

    class GameNotFoundError(ValueError):
        pass
