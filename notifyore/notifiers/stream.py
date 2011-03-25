import sys
from datetime import datetime
from pprint import pprint
from convoread.utils import wrap_string
from notifyore.notifiers import BaseNotifier

class StreamNotifier(BaseNotifier):

    def __init__(self, *args, **kwargs):
        # expects a kwarg: stream with a stream like object
        super(StreamNotifier, self).__init__(*args, **kwargs)
        self.format_string = kwargs.get('format','TODO')
        self.stream = kwargs.get('stream', sys.stdout)

    def format_message(self, message):
        message = self.normalize_message(message)
        username = message['n_user']
        kind = message.get('kind')
        created = None
        group = message['n_group']
        topic = message['n_topic']
        message_body = message['n_message']
        try:
            created = datetime.fromtimestamp(message['_ts'])
        except (KeyError, TypeError):
            pass
        if not created:
            try:
                created = datetime.fromtimestamp(message['date_created'])
            except (KeyError, TypeError):
                created = datetime.now()

        if len(topic) > 15:
            topic = topic[:15] + "..."


        if group and topic:
            label = "[{group}/{topic}]".format(**locals())
        else:
            label = ''
        body=wrap_string(message_body, indent=6).lstrip()
        time=created.strftime('%H:%M')
        # I know explicit is better than implicit - but I'm taking the lazy **locals route
        # in this limited context
        if kind == 'message':
            return '{time} <{username}> {label} {body}'.format(**locals())
        elif kind == 'topic':
            return '{time} <{username}> created new topic in #{group}: "{topic}"'.format(**locals())
        elif kind == 'mention':
            return '{time} <{username}> mentioned you: {label} {body}'.format(**locals())            
        elif kind == 'topic-delete':
            return '{time} <{username}> deleted a topic'.format(**locals())            
        else:
            return "{time} <{username}> [{group}]: {kind}".format(**locals())


    def handle_message(self, message):
        self.stream.write(self.format_message(message) + '\n')
        return True
        # kind = message['kind']
        # if kind == 'message':
            # out = self.format_message(message)
        # elif kind == 'topic':
            # pass
        # else:
            # out = kind
        # self.stream.write(out)
