import command_system
import vk_actions


chat_rules = '''Относитесь друг к другу с уважением. Сюда относятся персональные атаки, претензии, попытки ввода в заблуждение и т.п., не относящиеся к партиям в Политопии.
Если у вас есть к кому-то претензии, напишите ему или администратору (@quasistellar) в лс, а не в беседу. Если вы не уверены, нарушает ваше сообщение правила или нет, то лучше не писать его.
За нарушением следует предупреждение, а затем бан. И то и другое подтверждается @pyaive_oleg и @tampre во избежание предвзятых решений.'''


games_rules = '''Правила игр.

            1. Рестарты

            1.1. Игроки могут запросить рестарт игры, если их спавн рестартабелен, или если они используют бонусный рестарт.

            1.2. Спавн считается рестартабельным, если для захвата деревни до 5 хода не включительно:
            A. необходимо изучить технологию.
            B. нужно пересечь территорию противника.
            C. нужно замораживать воду (играя за Полярис).
            D. два игрока находятся на острове с 1 деревней.
            (достаточно выполнения 1 пункта)

            1.3. Перед запросом рестарта необходимо убедиться, что исследованы все возможные местоположения деревень.

            1.4. Бонусный рестарт: каждый игрок имеет 1 бонусный рестарт, его можно запросить до 5 хода включительно независимо от ситуации в игре.

            2. Тайм апы

            2.1 В случае тайм апа противника упомяните его здесь, приложив к сообщению скриншот его тайм апа.

            2.2 По истечении 6 часов после отправки сообщения, вы можете кикнуть противника и объявить о своей победе. Если противник был кикнут раньше срока, он вправе потребовать удаления игры.

            2.3 Если противник успел походить за дополнительные 6 часов, в следующий раз его можно кикать без предупреждения.

            3. Жульничество

            3.1. Использование не предусмотренных игрой способов получения игрового преимущества влечёт вечный бан в системе. К читерству относится накрутка звёзд, изменение карты, рестарты ходов для исследования территории, рестарты руин, спавна и т. п.'''


def rules(player_id, command_text, **kwargs):
    chat_rules_message = vk_actions.Message(text=chat_rules, disable_mentions=True)
    return [chat_rules_message, games_rules]


rules_command = command_system.Command(
    process=rules,
    keys=['правила', 'rules'],
    description='Правила игр',
    signature='',
    allow_users=True
)
