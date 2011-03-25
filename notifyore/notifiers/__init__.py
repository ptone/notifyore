from notifyore.notifiers.base import *
from notifyore.notifiers.growl import *
from notifyore.notifiers.stream import *

class RawNotifier(BaseNotifier):

    from pprint import pprint

    def handle_message(self, message):
        print message['kind']
        pprint(message)
        print '\n\n'
