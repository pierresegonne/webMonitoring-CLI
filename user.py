from data import data_utils
from data import messages as msg
from urllib.parse import urlparse


class User(object):

    acceptedSchemesUrls = ['http', 'https']
    modificationOpt = ['url', 'checkInterval']

    def __init__(self, username):

        self.username = username
        # key : website name | value : website instance
        self.mySites = {}


    def __str__(self):
        return ''

    def addWebsite(self, website):
        print(msg.website_add_welc)
        name = input(msg.website_add_name)
        while True:
            url = input(msg.website_add_url)
            if (self.checkUrl(url)):
                break
            print(msg.website_url_inc)
        while True:
            checkInterval = input(msg.website_add_check)
            if isinstance(checkInterval, int):
                checkInterval = int(checkInterval)
                break
            print(msg.website_add_check_inc)
        newWebsite = Website(name=name,url=url,checkInterval=checkInterval)
        self.mySites[name] = newWebsite
        # update the data about the user
        data_utils.updateUser(self)
        return

    def modifyWebsite(self, website):
        print(msg.website_modify_welc)
        self.displayWebsitesNames()
        # selection by name
        while True:
            name = input(msg.website_modify_name)
            if name in self.mySites:
                break
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
                if isinstance(newCheck, int):
                    newCheck = int(newCheck)
                    break
                print(msg.website_modify_inc)
            website.checkInterval = newCheck
        self.mySites[name] = website
        # update the data about the user
        data_utils.updateUser(self)
        return

    def deleteWebsite(self, website):
        print(msg.website_delete_welc)
        self.displayWebsitesNames()
        # selection by name
        while True:
            name = input(msg.website_delete_name)
            if name in self.mySites:
                break
            print(msg.website_delete_name_inc)
        # deletion of the website
        self.mySites.pop(name)
        # update the data about the user
        data_utils.updateUser(self)
        return

    def displayWebsitesNames(self):
        for websiteName in self.mySites.keys():
            print(websiteName)

    def checkUrl(self, url):
        objUrl = urlparse(url)
        return (objUrl.scheme in self.acceptedSchemesUrls)


class Website(object):

    # check interval in seconds
    def __init__(self,name,url, checkInterval = 10):
        self.name = name
        self.url = url
        self.checkInterval = checkInterval
        # monitoring
        self.log = {}