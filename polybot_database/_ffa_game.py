import db_utils as _db_utils
import polybot_utils as _polybot_utils
import utils as _utils


class FFAGame:

    _WINNER_ID_FOR_DRAW = 0  # TODO: It will cause problems in the future
    _MAX_DESCRIPTION_LENGTH = 32
    errors = None  # Will be set later

    def __init__(self, *, id: int, execute_query):
        self._execute = execute_query
        self._id = id
        # TODO: Probably should add _ensure_exists

    @property
    def id(self):
        return self._id

    @property
    def game_id(self):
        return self._get_field('game_id')

    @property
    def owner_id(self):
        return self._get_field('owner_id')

    @property
    def description(self):
        return self._get_field('description')

    @property
    def name(self):
        return self._get_field('name')

    @property
    def winner_id(self):
        return self._get_field('winner_id')

    @property
    def finish_time(self):
        return self._get_field('finish_time')

    def is_rated(self):
        return self._get_field('is_rated')

    def exists(self):
        [[does_exist]] = self._execute(
            'SELECT EXISTS'
            '(SELECT * FROM ffa_games WHERE game_id = %s);',
            [self._id]
        )
        return does_exist

    def change_description(self, new_description: str):
        self.verify_description(new_description)
        self._set_field('description', new_description)

    @classmethod
    def verify_description(cls, description: str):
        if not description:
            raise cls.errors.EmptyDescriptionError('game description can\'t be empty')
        if len(description) > cls._MAX_DESCRIPTION_LENGTH:
            raise cls.errors.DescriptionTooLongError('this description is too long')
        pass

    def add_member(self, player_id: int):
        if self.is_started():
            raise self.errors.AlreadyStartedError('can\'t add member if the game is already started')
        if self.has_member(player_id):
            raise self.errors.AlreadyMemberError('this player has already joined the game')
        self._execute(
            'INSERT ffa_memberships(member_id, game_id) VALUES (%s, %s);',
            [player_id, self._id]
        )

    def remove_member(self, player_id: int):
        if self.is_started():
            raise self.errors.AlreadyStartedError('can\'t remove member if the game is already started')
        if not self.has_member(player_id):
            raise self.errors.NotAMemberError('this player is not in the game')
        self._execute(
            'DELETE FROM ffa_memberships WHERE member_id = %s AND game_id = %s;',
            [player_id, self._id]
        )

    def has_member(self, player_id: int):
        [[result]] = self._execute(
            'SELECT EXISTS'
            '(SELECT * FROM ffa_memberships WHERE member_id = %s AND game_id = %s);',
            [player_id, self._id]
        )
        return result

    # Probably should not use "id" in the method name
    # because it sounds more like implementation detail.
    # It's easier to think about abstract members rather than their ids.
    def get_members(self):
        response = self._execute(
            'SELECT member_id FROM ffa_memberships WHERE game_id = %s;',
            self._id
        )
        [members_ids] = _utils.safe_zip(*response, result_length=1)
        return members_ids

    @property
    def members(self):
        return self.get_members()

    def delete(self):
        raise NotImplementedError

    def start(self, game_name: str):
        if self.is_started():
            raise self.errors.AlreadyStartedError('the game is already started')
        self._verify_game_name(game_name)
        self._set_field('name', game_name)

    def rename(self, new_game_name: str):
        self._verify_game_name(new_game_name)
        self._set_field('name', new_game_name)

    def _verify_game_name(self, game_name: str):
        if not _polybot_utils.is_game_name_correct(game_name):
            raise self.errors.InvalidGameNameError('this name can\'t be the name of game')

    def is_started(self):
        game_name = self._get_optional_field('name')
        return game_name is not None

    def finish(self, winner_id: int):
        if not self.has_member(winner_id):
            raise self.errors.NotAMemberError('specified winner is not in the game')
        if not self.is_started():
            raise self.errors.NotStartedError('unable to finish a game that has not been started')
        if self.is_finished():
            raise self.errors.AlreadyFinishedError('the game is already finished')
        self._set_field('winner_id', winner_id)
        self._execute(
            'UPDATE ffa_games SET finish_time = UNIX_TIMESTAMP() WHERE game_id = %s;',
            [self._id]
        )

    def is_finished(self):
        winner = self._get_optional_field('winner_id')
        return winner is not None

    def finish_with_draw(self):
        return self.finish(winner_id=self._WINNER_ID_FOR_DRAW)

    # TODO: Generalize and move out

    def _get_optional_field(self, field_name):
        query = 'SELECT {field_name} FROM ffa_games WHERE game_id = %s;'
        query = _db_utils.format_identifiers(query, field_name=field_name)
        [[field_value]] = self._execute(query, [self._id])
        return field_value

    def _get_field(self, field_name):
        result = self._get_optional_field(field_name)
        if result is None:
            raise ValueError(f'"{field_name}" field is empty (None/NULL), unable to get it\'s value')
        return result

    def _set_field(self, field_name, new_value):
        query = 'UPDATE ffa_games SET {field_name} = %s WHERE game_id = %s;'
        query = _db_utils.format_identifiers(query, field_name=field_name)
        self._execute(query, [new_value, self._id])


class _FFAGameErrors:

    def __init__(self):
        pass

    class InvalidDescriptionError(ValueError):
        pass

    class EmptyDescriptionError(InvalidDescriptionError):
        pass

    class DescriptionTooLongError(InvalidDescriptionError):
        pass

    class InvalidGameNameError(ValueError):
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

FFAGame.errors = _FFAGameErrors
