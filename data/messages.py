import datetime
# Thanks to http://www.network-science.de/ascii/ for the generation of titles

# User menu
user_menu_welc1 = '\n==== Welcome to the user menu {'
user_menu_welc2 = '} ===='
user_menu_description = 'You can manage here the websites you want to monitor'
user_menu_commands = 'Available commands - '
user_menu_command_inc = '\n! Incorrect Command !'
user_menu_help = '\n mysites - display the names and urls of sites already added' \
                 '\n add - add a new website to monitor' \
                 '\n modify - modify an already added website' \
                 '\n delete - delete a website from the list of monitored websites'
user_menu_exit = 'See you Soon !'

# Website addition
website_add_welc = '\nWelcome to the Website addition interface !'
website_add_name = 'What name do you want to give to this url? '
website_add_url = 'What is the url you want to associate to this name? '
website_add_check = 'What check interval do you want to define ? (in seconds, default 10s) '
website_add_check_inc = '\n! Incorrect check interval, must be an integer !'



# Website modification 
website_modify_welc = '\nWelcome to the Website modification interface (exit) !\nHere are your websites :\n'
website_modify_name = 'What website do you want to modify? [name] '
website_modify_name_inc = '! Unknown name !'
website_modify_opt = 'What do you want to modify ? '
website_modify_inc = '\n! Incorrect !'
website_modify_url = 'What is the new url? '
website_modify_check = 'What is the new check interval ? (in seconds) '



# Website deletion
website_delete_welc = '\nWelcome to the Website deletion interface (exit) !\nHere are your websites :\n'
website_delete_name = 'What website do you want to delete? [name] '
website_delete_name_inc = '! Unknown name !'

# Website general
website_url_inc = '\n! Incorrect url !'


# =============================================
# Monitoring ==================================
# =============================================

# Curses display access
init_monitoring_usernotfound = '\n! Unknown user, please create this user before continuing !'

# Curses goodbye
curses_goodbye_height = 4
curses_goodbye_1 = '    ____________  __  ______  __  __  ________  ____  _  __'
curses_goodbye_2 = '  / __/ __/ __/  \ \/ / __ \/ / / / / __/ __ \/ __ \/ |/ /'
curses_goodbye_3 = ' _\ \/ _// _/     \  / /_/ / /_/ / _\ \/ /_/ / /_/ /    / '
curses_goodbye_4 = '/___/___/___/     /_/\____/\____/ /___/\____/\____/_/|_/   '

# Curses window
window_title = 'WEBMONITORING'
window_title_1 = ' _      _________    __  _______  _  ________________  ___ '
window_title_2 = '| | /| / / __/ _ )  /  |/  / __ \/ |/ /  _/_  __/ __ \/ _ \\'
window_title_3 = '| |/ |/ / _// _  | / /|_/ / /_/ /    // /  / / / /_/ / , _/'
window_title_4 = '|__/|__/___/____/ /_/  /_/\____/_/|_/___/ /_/  \____/_/|_| '
window_author = 'P.SEGONNE'
window_monitoring_title = 'MONITORING'
window_monitoring_tenMin = '10 min'
window_monitoring_hour = '1 hour'
window_alert_title = 'ALERTS'
window_quit = 'Press \'q\' to exit'
window_default_stat = '…'


# Curses Alerts
def alert2string(alert_obj):
    # "Website {website} is down. availability={availablility}, time={time}"
    return 'Website ' + alert_obj['website'] + ' is ' +alert_obj['status'].lower() + '. ' + ' Availability=' + str(alert_obj['availability']) + ', time=' + str(datetime.datetime.fromtimestamp(alert_obj['time']).strftime('%Y-%m-%d %H:%M:%S'))

# Mail alert
def alert2subject(alert_obj):
    return '[WEBMONITOR] WEBSITE : ' + alert_obj['website'] + ' IS ' + alert_obj['status']

# Curses errors
window_err_height = '\n!! Cannot init the screen, height insufficient !!\n'
window_err_width = '\n!! Cannot init the screen, width insufficient !!\n'
curses_cursor_inv = '\n!! Invisible cursor not supported !!\n'

