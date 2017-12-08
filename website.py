class Website(object):
    """Class for website representation

    """


    # check interval in seconds, default 10
    def __init__(self, name, url, checkInterval=10):
        self.name = name
        self.url = url
        self.checkInterval = checkInterval
        # monitoring logs
        self.log = {}

    def __str__(self):
        """
        Enhances Readability
        :return:
        """
        return ('[Name : ' + self.name + ' ] [ Url : ' + self.url + ' ]')