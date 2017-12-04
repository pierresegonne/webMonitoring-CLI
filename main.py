import argparse
import user
import display_curses

def openUserManagement(username):
    user.userMenu(username)

def openMonitoring(username):
    display_curses.WebmonitoringCurses(username)


parser = argparse.ArgumentParser(description='CLI App for web Monitoring')

subparser = parser.add_subparsers(help='Reachable Interfaces', dest='cmd')
parser_u = subparser.add_parser('user', help='User help')
parser_u.add_argument('username_u', type=str, action='store')

parser_m = subparser.add_parser('monitor', help='Monitor help')
parser_m.add_argument('username_m', type=str, action='store')


args = parser.parse_args()

if (args.cmd == 'user'):
    openUserManagement(args.username_u)

if (args.cmd == 'monitor'):
    openMonitoring(args.username_m)



