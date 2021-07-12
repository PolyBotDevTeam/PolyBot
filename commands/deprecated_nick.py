import command_system


def deprecated_nick(player_id, command_text):
    player_command = command_system.get_command('/player')
    message_about_this_command = 'Данная команда устарела. Если вы хотели изменить ваш никнейм, вам следует использовать команду /сменить_ник'
    return list(player_command(player_id, command_text)) + [message_about_this_command]


# TODO: make this command just for nickname, not for whole player info
registration_command = command_system.UserCommand()

registration_command.keys = ['ник', 'никнейм', 'nick', 'nickname']
registration_command.description = ' никнейм - Устаревшая команда. Вместо неё следует использовать /сменить_ник никнейм'
registration_command.process = deprecated_nick
