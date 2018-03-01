

class Message:  # pragma:nocover
    def __init__(self, from_address, to_address, fullmessage, **kwargs):
        self.from_address = from_address
        self.to_address = to_address
        self.fullmessage = fullmessage


class SMTP:  # pragma:nocover
    inbox = []
    has_quit = False

    def __init__(self, *args, **kwargs):
        pass

    def ehlo(self):
        pass

    def starttls(self):
        pass

    def login(self, username, password):
        self.username = username
        self.password = password

    def sendmail(self, from_address, to_address, fullmessage):
        self.inbox.append(Message(from_address, to_address, fullmessage))
        return []

    def quit(self):
        self.has_quit = True
