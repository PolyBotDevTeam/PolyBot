import utils as _utils


class FFAGame:

    _WINNER_ID_FOR_DRAW = 0

    def __init__(self, *, game_id: int, execute_query):
        self._execute = execute_query
        self._game_id = game_id  # TODO: Probably should rename to just self._id
        self._errors = _FFAGameErrors()
        # TODO: Probably should add _ensure_exists

    @property
    def errors(self):
        return self._errors

    def exists(self):
        [[does_exist]] = self._execute(
            'SELECT EXISTS'
            '(SELECT * FROM ffa_games WHERE game_id = %s);',
            [self._game_id]
        )
        return does_exist

    def add_member(self, player_id: int):
        if self.is_started():
            raise self.errors.AlreadyStartedError('can\'t add member if the game is already started')
        if self.has_member(player_id):
            raise self.errors.AlreadyMemberError('this player has already joined the game')
        self._execute(
            'INSERT ffa_memberships(member_id, game_id) VALUES (%s, %s);',
            [player_id, self._game_id]
        )

    def remove_member(self, player_id: int):
        if self.is_started():
            raise self.errors.AlreadyStartedError('can\'t remove member if the game is already started')
        if not self.has_member(player_id):
            raise self.errors.NotAMemberError('this player is not in the game')
        self._execute(
            'DELETE FROM ffa_memberships WHERE member_id = %s AND game_id = %s;',
            [player_id, self._game_id]
        )

    def has_member(self, player_id: int):
        [[result]] = self._execute(
            'SELECT EXISTS'
            '(SELECT * FROM ffa_memberships WHERE member_id = %s AND game_id = %s);',
            [player_id, self._game_id]
        )
        return result

    # Probably should not use "id" in the method name
    # because it sounds more like implementation detail.
    # It's easier to think about abstract members rather than their ids.
    def get_members(self):
        response = self._execute(
            'SELECT member_id FROM ffa_memberships WHERE game_id = %s;',
            self._game_id
        )
        [members_ids] = _utils.safe_zip(*response)
        return members_ids

    def delete(self):
        raise NotImplementedError

    def start(self, game_name: str):
        if self.is_started():
            raise self.errors.AlreadyStartedError('the game is already started')
        self._set_field('game_name', game_name)

    def is_started(self):
        game_name = self._get_field('game_name')
        return game_name is not None

    def finish(self, winner_id: int):
        if not self.is_started():
            raise self.errors.NotStartedError('unable to finish a game that has not been started')
        if self.is_finished():
            raise self.errors.AlreadyFinishedError('the game is already finished')
        self._set_field('winner_id', winner_id)

    def is_finished(self):
        winner = self._get_field('winner_id')
        return winner is not None

    def finish_with_draw(self):
        return self.finish(winner_id=self._WINNER_ID_FOR_DRAW)

    def _get_field(self, field_name):
        [[field_value]] = self._execute(
            'SELECT %s FROM ffa_games WHERE game_id = %s;',
            [field_name, self._game_id]
        )
        return field_value

    def _set_field(self, field_name, new_value):
        self._execute(
            'UPDATE ffa_games SET %s = %s WHERE game_id = %s;',
            [field_name, new_value, self._game_id]
        )


class _FFAGameErrors:

    def __init__(self):
        pass

    class AlreadyMemberError(ValueError):
        pass

    class NotAMemberError(ValueError):
        pass

    class AlreadyStartedError(ValueError):
        pass

    class NotStartedError(ValueError):
        pass

    class AlreadyFinishedError(ValueError):
        pass
