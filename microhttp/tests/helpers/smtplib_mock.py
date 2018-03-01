

class Message:  # pragma:nocover
    def __init__(self, from_address, to_address, fullmessage, **kwargs):
        self.from_address = from_address
        self.to_address = to_address
        self.fullmessage = fullmessage


class SMTP:  # pragma:nocover
    __slots__ = ('inbox', 'username', 'password', 'has_quit',)

    def __init__(self, *args, **kwargs):
        pass

    def ehlo(self):
        pass

    def starttls(self):
        pass

    @classmethod
    def login(cls, username, password):
        cls.username = username
        cls.password = password

    @classmethod
    def sendmail(cls, from_address, to_address, fullmessage):
        if type(cls.inbox) is not list:
            cls.inbox = []
        cls.inbox.append(Message(from_address, to_address, fullmessage))
        return []

    @classmethod
    def quit(cls):
        cls.has_quit = True
