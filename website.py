class Website(object):
    # check interval in seconds
    def __init__(self, name, url, checkInterval=10):
        self.name = name
        self.url = url
        self.checkInterval = checkInterval
        # monitoring
        self.log = {}

    def __str__(self):
        return ('[Name : ' + self.name + ' ] [ Url : ' + self.url + ' ]')