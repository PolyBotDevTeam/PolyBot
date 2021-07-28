class FFAGames:

    def __init__(self, execute_query):
        self._execute = execute_query
        self._errors = _FFAGamesErrors()

    @property
    def errors(self):
        return self._errors

    def create_game(self, owner_id, description):
        [[game_id]] = self._execute(
            'INSERT ffa_games(owner_id, description) VALUES (%s, %s);\n'
            'SELECT LAST_INSERT_ID();'
            [owner_id, description]
        )
        return game_id

    def delete_game(self, game_id):
        raise NotImplementedError

    def does_game_exist(self, game_id):
        raise NotImplementedError

    def ensure_game_exists(self, game_id):
        if not self.does_game_exist(game_id):
            raise self.errors.GameNotFoundError('the game with this id does not exist')

    def add_player_to_game(self, player_id, game_id):
        if self.is_member(player_id, game_id):
            raise self.errors.AlreadyMemberError('this player has already joined the game')
        self._execute(
            'INSERT ffa_memberships(member_id, game_id) VALUES (%s, %s);',
            [player_id, game_id]
        )

    def remove_player_from_game(self, player_id, game_id):
        if not self.is_member(player_id, game_id):
            raise self.errors.NotMemberError('this player is not in the game')
        self._execute(
            'DELETE FROM ffa_memberships WHERE member_id = %s AND game_id = %s;',
            [player_id, game_id]
        )

    def is_member(self, player_id, game_id):
        self.ensure_game_exists(game_id)
        [[result]] = self._execute(
            'SELECT EXISTS'
            '(SELECT * FROM ffa_memberships WHERE member_id = %s AND game_id = %s);'
            [player_id, game_id]
        )
        return result

    # Probably should not use "id" in the method name
    # because it sounds more like implementation detail.
    # It's easier to think about abstract members rather than their ids.
    def get_game_members(self, game_id):
        self.ensure_game_exists(game_id)
        response = self._execute(
            'SELECT member_id FROM ffa_memberships WHERE game_id = %s;',
            game_id
        )
        [members_ids] = utils.safe_zip(*response)
        return members_ids

    def start_game(self, game_id, game_name):
        raise NotImplementedError

    def finish_game(self, game_id, winner):
        raise NotImplementedError

    def get_games_of_player(self, player_id):
        raise NotImplementedError


class _FFAGamesErrors:

    def __init__(self):
        pass

    class GameNotFoundError(ValueError):
        pass

    class AlreadyMemberError(ValueError):
        pass

    class NotAMemberError(ValueError):
        pass
