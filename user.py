from data import data_utils
from data import messages as msg
from urllib.parse import urlparse
from website import Website

def userMenu(username):
    currentUser = data_utils.getUser(username)
    if not currentUser:
        currentUser = User(username)
    print(msg.user_menu_welc1 + username + msg.user_menu_welc2)
    commands = ['mysites', 'add', 'modify', 'delete', 'help', 'exit']
    print(msg.user_menu_description)
    while True:
        cmd = input('\n' + msg.user_menu_commands + str(commands) + '\n')
        if cmd not in commands:
            print(msg.user_menu_command_inc)
            continue
        elif cmd == 'exit':
            print(msg.user_menu_exit)
            break
        elif cmd == 'mysites':
            currentUser.displayWebsites()
        elif cmd == 'add':
            currentUser.addWebsite()
        elif cmd == 'modify':
            currentUser.modifyWebsite()
        elif cmd == 'delete':
            currentUser.deleteWebsite()
        elif cmd == 'help':
            print(msg.user_menu_help)
    return


class User(object):

    acceptedSchemesUrls = ['http', 'https']
    modificationOpt = ['url', 'checkInterval']

    def __init__(self, username):

        self.username = username
        # key : website name | value : website instance
        self.mySites = {}


    def __str__(self):
        return ''

    def addWebsite(self):
        print(msg.website_add_welc)
        name = input(msg.website_add_name)
        while True:
            url = input(msg.website_add_url)
            if (self.checkUrl(url)):
                break
            print(msg.website_url_inc)
        while True:
            checkInterval = input(msg.website_add_check)
            try:
                checkInterval = int(checkInterval)
                break
            except :
                print(msg.website_add_check_inc)
        newWebsite = Website(name=name,url=url,checkInterval=checkInterval)
        self.mySites[name] = newWebsite
        # update the data about the user
        data_utils.updateUser(self)
        return

    def modifyWebsite(self):
        print(msg.website_modify_welc)
        self.displayWebsites()
        # selection by name
        while True:
            name = input(msg.website_modify_name)
            if name in self.mySites:
                break
            if name == 'exit':
                return
            print(msg.website_modify_name_inc)
        website = self.mySites[name]
        # modif opts
        while True:
            opt = input(msg.website_modify_opt + str(self.modificationOpt))
            if opt in self.modificationOpt:
                break
            print(msg.website_modify_inc)
        # todo refactor make if adaptable
        if opt == 'url':
            while True:
                newUrl = input(msg.website_modify_url)
                if self.checkUrl(newUrl):
                    break
                print(msg.website_url_inc)
            website.url = newUrl
        if opt == 'checkInterval':
            while True:
                newCheck = input(msg.website_modify_check)
                try:
                    newCheck = int(newCheck)
                    break
                except :
                    print(msg.website_modify_inc)
            website.checkInterval = newCheck
        self.mySites[name] = website
        # update the data about the user
        data_utils.updateUser(self)
        return

    def deleteWebsite(self):
        print(msg.website_delete_welc)
        self.displayWebsites()
        # selection by name
        while True:
            name = input(msg.website_delete_name)
            if name in self.mySites:
                break
            if name == 'exit':
                return
            print(msg.website_delete_name_inc)
        # deletion of the website
        self.mySites.pop(name)
        # update the data about the user
        data_utils.updateUser(self)
        return

    def displayWebsites(self):
        print('\nYour Websites :')
        for websiteName in self.mySites.keys():
            print(str(self.mySites[websiteName]))

    def checkUrl(self, url):
        objUrl = urlparse(url)
        return (objUrl.scheme in self.acceptedSchemesUrls)