from pprint import pprint

class Dispatcher(object):

    def __init__(self, settings, convore):
        self.convore = convore
        self.settings = settings
        self.rules = []

    def dispatch_message(self, message):
        for rule in self.rules:
            # pprint (message)
            # continue
            if rule.handle_message(message):
                # if a rule handles the message, it returns true
                return

