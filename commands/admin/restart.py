import command_system
import sys


def _process_restart_command(player_id, command_text, **kwargs):
    # TODO: yield RestartAction()
    sys.exit()


restart_command = command_system.Command(
    process=_process_restart_command,
    keys=['restart'],
    description='Перезапустить бота',
    signature='',
    allow_users=False
)
