import smtplib
from data import messages as msg

mailrecipient = ''

class MailSender(object):
    """Class that allows the sending of alerts via mail.
    To change recipient simply modifiy the mailrecipient field
    """

    def __init__(self, recipient):
        self.TO = recipient

        # Gmail Sign In
        self.gmail_sender = 'webmonitoringcli@gmail.com'
        self.gmail_passwd = 'DataDogIsAwesome'

    def sendAlert(self, alert):
        """
        Sends mail via smtp server
        :param alert:
        :return:
        """
        if len(self.TO) > 0:
            # SERVER
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.login(self.gmail_sender, self.gmail_passwd)

            # Content
            SUBJECT = msg.alert2subject(alert)
            TEXT = msg.alert2string(alert)

            BODY = '\r\n'.join(['To: %s' % self.TO,
                                'From: %s' % self.gmail_sender,
                                'Subject: %s' % SUBJECT,
                                '', TEXT])

            try:
                server.sendmail(self.gmail_sender, [self.TO], BODY)
            except:
                print('error sending mail')

            server.quit()

        return





