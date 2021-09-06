class Players:

    def __init__(self, *, execute_query):
        self._execute = execute_query

    def is_registered(self, player_id: int):
        [[result]] = self._execute(
            'SELECT EXISTS'
            '(SELECT * FROM players WHERE player_id = %s);',
            player_id
        )
        return result
