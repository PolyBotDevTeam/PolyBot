import command_system
import settings


guide_text = '''Гайд по пользованию ботом.

Для начала вам необходимо зарегистрироваться в системе. \
Для этого отправьте сообщение вида </регистрация Nickname>, указав свой никнейм. \
Его можно найти в Throne Room прямо в игре.

Каждый игрок начинает с рейтингом 1050 : 950. На первое число влияют игры, где вы ходите первым, на второе - вторым.

Давайте посмотрим, есть ли желаюшие поиграть? \
Напишите </игры>. \
Вы можете присоединиться к игре командой </войти айди_игры>. \
Противник создаст игру и пригласит вас в неё.

Если же открытых игр нет, вы можете начать свою. \
Используйте команду </открыть описание_игры>. \
В описании можно указать такие подробности как размер карты, режим игры и доступные племена. \
После того как противник присоединится, вы получите уведомление. \
Добавьте противника в друзья в Политопии, создайте игру, \
после чего напишите команду </начать айди_игры Название_Игры>, \
указав, соответственно, ID игры и её название в Политопии.

Когда игра завершится, воспользуйтесь командой </победил я айди_игры> или </победил противник айди_игры>. \
Если победили вы, убедитесь, что ваш противник тоже использовал команду и ваша победа зачлась.

Посмотреть список оконченных игр можно с помощью команды </завершённые>, неоконченных - </текущие>.

Список игроков с наивысшим рейтингом покажет команда </топ>.
Приятной игры!'''.replace('<', f'[club{settings.group_id}|').replace('>', ']')


def guide(player_id, command_text):
    return [guide_text]


guide_command = command_system.UserCommand()

guide_command.keys = ['гайд', 'guide']
guide_command.description = ' - Гайд по пользованию ботом.'
guide_command.process = guide
