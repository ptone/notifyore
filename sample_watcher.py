import time
from notifyore import Dispatcher, Rule, EnhancedConvore
from notifyore.notifiers import StreamNotifier, RawNotifier

# uncomment for growl:
# from notifyore.notifiers import GrowlNotifier

convore = EnhancedConvore()
dispatcher = Dispatcher({},convore)
# uncomment for growl:
# growl = GrowlNotifier(convore)
console = StreamNotifier(convore)
raw = RawNotifier(convore)
dispatcher.rules = [
        # mention of me anywhere
        Rule(convore,   match_events = ['mention'],
                        actions = [console]),
        # eric talking in API group
        Rule(convore,   match_events = ['message', 'topic'],
                        match_attributes={
                            'group':'convore-api-developers',
                            'user':'ericflo'},
                        actions = [console]),

        # leah talking in API group, notice dupe rule for "OR"
        Rule(convore,   match_events = ['message', 'topic'],
                        match_attributes={
                            'group':'convore-api-developers',
                            'user':'leah'},
                        actions = [console]),

        # Any stars I get!
        Rule(convore,   match_events = ['star'],
                        match_attributes={
                            'starred_user':'ptone'},
                        actions = [console]),

        # Any message in my groups mentioning cheese
        Rule(convore,   match_attributes={
                            'message_search':'cheese'},
                        actions = [console])
        ]

convore.on_live_update(dispatcher.dispatch_message)
print "Running...."
while True:
    # TODO I know, we need a better console entry script
    # print 'waiting'
    time.sleep(15)
