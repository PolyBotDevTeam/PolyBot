import command_system


def _process_hey_command(actor_id, command_text, **kwargs):
    return ['Я жива!']


hey_command = command_system.Command(
    process=_process_hey_command,
    keys=['ау', 'эй', 'ало', 'алло', 'алё', 'тест', 'hey', 'test'],
    description='Поторопить бота',
    signature='',
    allow_users=True
)
