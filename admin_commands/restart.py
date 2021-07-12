import command_system
import sys


def restart(player_id, command_text):
    sys.exit()


restart_command = command_system.AdminCommand()

restart_command.keys = ['restart']
restart_command.description = ' - Остановить процесс с полиботом, чтобы он запустился заново.'
restart_command.process = restart
