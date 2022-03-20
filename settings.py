import json
import os
import sys


project_folder = os.path.dirname(os.path.abspath(__file__))


with open(os.path.join(project_folder, 'settings.json'), 'r') as fp:
    settings = json.load(fp)


token = settings['token']
group_id = settings['group_id']

user = settings['user']
password = settings['password']
host = settings['host']
database = settings['database']


admins_ids = tuple(settings['admins_ids'])
admin_chats = tuple(settings['admin_chats_ids'])

main_chat_id = settings['main_chat_id']
polydev_chat_id = settings['polydev_chat_id']
tournament_chat_id = settings['tournament_chat_id']

errors_log_file = sys.stdout
commands_log_file = open(os.path.join(project_folder, 'logs', 'commands_log.txt'), 'a')
