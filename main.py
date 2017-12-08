import argparse
import user
import display_curses

def openUserManagement(username):
    """
    Acces to the user management side of the application
    :param username:
    :return:
    """
    user.userMenu(username)

def openMonitoring(username):
    """
    Access to the monitoring display
    :param username:
    :return:
    """
    display_curses.WebmonitoringCurses(username)

# ==============================================================
# CMD HANDLING =================================================
# Through argparse =============================================
# ==============================================================


parser = argparse.ArgumentParser(description='CLI App for web Monitoring')

subparser = parser.add_subparsers(help='Reachable Interfaces', dest='cmd')

# Parser for the user interface
parser_u = subparser.add_parser('user', help='User help')
parser_u.add_argument('username_u', type=str, action='store')

# Parser for the monitoring interface
parser_m = subparser.add_parser('monitor', help='Monitor help')
parser_m.add_argument('username_m', type=str, action='store')

# Cmd that gets the command from the command line
args = parser.parse_args()

if (args.cmd == 'user'):
    openUserManagement(args.username_u)

if (args.cmd == 'monitor'):
    openMonitoring(args.username_m)



