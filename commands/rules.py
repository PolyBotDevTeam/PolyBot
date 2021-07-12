import command_system


def rules(player_id, command_text):
    message = 'Правила игр.\n\n \
            1. Рестарты\n\n \
            1.1. Игроки могут запросить рестарт игры, если их спавн рестартабелен, или если они используют бонусный рестарт.\n\n \
            1.2. Спавн считается рестартабельным, если для захвата деревни до 5 хода не включительно:\n \
            A. необходимо изучить технологию.\n \
            B. нужно пересечь территорию противника.\n \
            C. нужно замораживать воду (играя за Полярис).\n \
            D. два игрока находятся на острове с 1 деревней.\n \
            (достаточно выполнения 1 пункта)\n\n \
            1.3. Перед запросом рестарта необходимо убедиться, что исследованы все возможные местоположения деревень.\n\n \
            1.4. Бонусный рестарт: каждый игрок имеет 1 бонусный рестарт, его можно запросить до 5 хода включительно независимо от ситуации в игре.\n\n \
            2. Тайм апы\n\n \
            2.1 В случае тайм апа противника упомяните его здесь, приложив к сообщению скриншот его тайм апа.\n\n \
            2.2 По истечении 6 часов после отправки сообщения, вы можете кикнуть противника и объявить о своей победе. Если противник был кикнут раньше срока, он вправе потребовать удаления игры.\n\n \
            2.3 Если противник успел походить за дополнительные 6 часов, в следующий раз его можно кикать без предупреждения.\n\n \
            3. Жульничество\n\n \
            3.1. Использование не предусмотренных игрой способов получения игрового преимущества влечёт вечный бан в системе. К читерству относится накрутка звёзд, изменение карты, рестарты ходов для исследования территории, рестарты руин, спавна и т. п..'
    return [message]


rules_command = command_system.UserCommand()

rules_command.keys = ['правила', 'rules']
rules_command.description = ' - Правила игр.'
rules_command.process = rules
