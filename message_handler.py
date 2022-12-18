# Deprecated module

import functools

import vk_api
import pymysql

from command_parsing_utils import try_to_identify_id as _try_to_identify_id
import vk_utils
import settings


_session = vk_api.VkApi(token=settings.token)
_api = _session.get_api()
fetch_usernames = functools.partial(vk_utils.fetch_usernames, vk=_api)
username = functools.partial(vk_utils.fetch_username, vk=_api)
create_mention = functools.partial(vk_utils.create_mention, vk=_api)
try_to_identify_id = functools.partial(_try_to_identify_id, vk=_api)

def create_connection():
    connection = pymysql.connect(
        host=settings.host,
        user=settings.user,
        password=settings.password,
        database=settings.database,
        autocommit=True
    )
    return connection

