import functools

from vk_api.bot_longpoll import VkBotEventType

import vk_actions
import vk_utils


class PolyBot:

    def __init__(self, *, vk, database, settings, message_handler, command_system):
        self._vk = vk
        self._database = database
        self._settings = settings
        self._message_handler = message_handler
        self._command_system = command_system
        self._autoconfirmer_data = {'latest_autoconfirm_time': 0}

    def process_vk_event(self, vk_event):
        vk = self._vk

        if vk_event.type != VkBotEventType.MESSAGE_NEW:
            return

        message = vk_event.obj.message

        # TODO: Move to command system?
        if message['text'].lower().replace('"', '').replace('?', '') == 'что такое эло':
            return self._process_command('!what_is_elo', peer_id=message['peer_id'])

        if vk_event.from_chat:
            self._process_message_from_chat(message)

    def _process_message_from_chat(self, message):
        vk = self._vk
        database = self._database

        chat_id = vk_utils.chat_id_by_peer_id(message['peer_id'])

        if chat_id in {self._settings.main_chat_id, self._settings.tournament_chat_id}:
            if chat_id == self._settings.main_chat_id:
                template = polybot_welcome
            else:
                assert chat_id == self._settings.tournament_chat_id
                template = 'Привет, {username}!\nПрочитай правила в закреплённом сообщении.'

            action = message.get('action')
            if action is not None and action['type'] == 'chat_invite_user_by_link':
                username = vk_utils.fetch_username(message['from_id'], vk=vk).split()[0]
                text = template.format(username=username)
                self._message_handler.send_message(text, vk=vk, chat_id=chat_id)

        triggering_prefixes = {'/', '!'}
        text = message['text']

        if not any(text.startswith(prefix) for prefix in triggering_prefixes):
            return

        assert text
        prefix = text[0]
        user_command = text

        message_time = message['date']
        actor = message['from_id']

        for file in [settings.commands_log_file, settings.errors_log_file]:
            print(message_time, actor, repr(text), sep='\n', end='\n\n', file=file, flush=True)

        if user_command == '!restart' and actor in settings.admins_ids and chat_id in settings.admin_chats:
            sys.exit()

        def _are_commands_equal(command_str_1, command_str_2):
            prefix_1, name_1, command_text_1 = self._command_system.parse_command(command_str_1)
            prefix_2, name_2, command_text_2 = self._command_system.parse_command(command_str_2)
            try:
                names_1 = self._command_system.get_command(prefix_1+name_1).keys
            except self._command_system.CommandNotFoundError:
                names_1 = []
            return prefix_1 == prefix_2 and name_2 in names_1

        # TODO: command attr "admin_chat_required"
        if chat_id not in settings.admin_chats:
            whitelisted_commands = ['/спать', '/выбор_племени', '!py']
            is_command_whitelisted = any(_are_commands_equal(user_command, x) for x in whitelisted_commands)
            if not is_command_whitelisted:
                return

        return self._process_command(
            user_command,
            actor=actor,
            command_source_message=message,
            chat_id=chat_id
        )

    def process_new_time(self, new_time):
        if new_time - self._autoconfirmer_data['latest_autoconfirm_time'] < 60*60:
            return
        self._autoconfirm_outdated_wins()
        self._autoconfirmer_data['latest_autoconfirm_time'] = new_time

    def _autoconfirm_outdated_wins(self):
        return self._process_command('!autoconfirm_outdated_wins', chat_id=self._settings.main_chat_id)

    def _process_command(self, command, *, actor=None, command_source_message=None, **message_sending_kwargs):
        if actor is None:
            actor = -self._settings.group_id
        vk = self._vk

        actions = self._command_system.process_command(
            actor,
            command,
            command_source_message,
            process_exception=functools.partial(self._message_handler.process_exception, vk=vk),
            database=self._database,
            vk=vk
        )
        self._execute_actions(actions, vk=vk, **message_sending_kwargs)

    # TODO: Probably should move out
    def _execute_actions(self, actions, **message_sending_kwargs):
        for action in actions:
            if isinstance(action, vk_actions.Message):
                self._message_handler.send_message(message=action, vk=self._vk, **message_sending_kwargs)
            else:
                raise TypeError('unknown action type:', type(action))


polybot_welcome = """Приветствую, {username}!

Чтобы зарегистрироваться в боте, отправьте сообщение </регистрация Nickname>, указав вместо Nickname свой ник в Политопии."""

polybot_welcome = vk_utils.highlight_marked_text_areas(polybot_welcome)

