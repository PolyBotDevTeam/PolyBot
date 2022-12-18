import command_system
import elo


def recalculate(player_id, command_text, *, database, **kwargs):
    elo.recalculate(database=database)
    return ['Рейтинг обновлён.']


recalculate_command = command_system.Command(
    process=recalculate,
    keys=['recalculate'],
    description='Перерасчёт рейтинга',
    signature='',
    allow_users=False
)
