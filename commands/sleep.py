import command_system


def sleep(player_id, command_text):
    message = 'Пора спать. Макар Пустовалов сказал.'
    return [message]


sleep_command = command_system.UserCommand()

sleep_command.keys = ['спать', 'sleep']
sleep_command.description = ' - Вероятно, уже пора.'
sleep_command.process = sleep
