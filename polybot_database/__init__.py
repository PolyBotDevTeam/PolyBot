import database.ffa_games as _ffa_games_module


# TODO: should also create database.players, database.games etc.


class PolyBotDatabase:

    def __init__(self, create_connection):
        self._create_connection = create_connection
        self._connection = self._create_connection()
        self._ffa_games = _ffa_games_module.FFAGames(execute_query=self._execute_query)

    def _execute_query(self, query, args):
        cursor = self._connection.cursor()
        cursor.execute(query, args)
        return cursor

    @property
    def ffa_games(self):
        return self._ffa_games
