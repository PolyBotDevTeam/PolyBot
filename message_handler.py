import warnings as _warnings

_warnings.warn(
    'message_handler module is deprecated. '
    'Never create new imports of this module, '
    'and preferably remove old ones.',
    DeprecationWarning
)


from functools import partial as _partial

import vk_api as _vk_api
import pymysql as _pymysql

from command_parsing_utils import try_to_identify_id as _try_to_identify_id
import vk_utils as _vk_utils
import settings as _settings


_session = _vk_api.VkApi(token=_settings.token)
_api = _session.get_api()
fetch_usernames = _partial(_vk_utils.fetch_usernames, vk=_api)
username = _partial(_vk_utils.fetch_username, vk=_api)
create_mention = _partial(_vk_utils.create_mention, vk=_api)
try_to_identify_id = _partial(_try_to_identify_id, vk=_api)


def create_connection():
    connection = _pymysql.connect(
        host=_settings.host,
        user=_settings.user,
        password=_settings.password,
        database=_settings.database,
        autocommit=True
    )
    return connection
