
class BaseNotifier(object):
    """
    base class for objects that take notification actions
    """

    def __init__(self, convore):
        self.convore = convore
        # TODO, build reference datastructures here
        
    def handle_message(self, message):
        """
        handles a single message from convore and creates notification
        """
        raise NotImplementedError

    def normalize_message(self, message):
        """
        adds a consistent, shallow set of fields to the message dict
        focused on:
        n_user -> username
        n_topic -> topic name
        n_group -> group name

        also adds:
        n_mentioned_user
        n_starred_user
        slugs used where name not available
        """

        kind = message['kind']

        # all user fields are the same across kinds
        if 'user' in message:
            message['n_user'] = message['user']['username']
        else:
            message['n_user'] = '(no-user)'

        message['n_message'] = ''
        message['n_group'] = ''
        message['n_topic'] = ''

        if kind == 'message':
            message['n_topic'] = message['topic']['name']
            message['n_group'] = self.convore.get_groups()[message['group']]['name']
            message['n_message'] = message['message']
        elif kind == 'message-delete':
            message['n_message'] = '<deleted>'
            message['n_topic'] = message['n_group'] = 'unknown'
        elif kind == 'topic':
            message['n_topic'] = message['name']
            message['n_group'] = self.convore.get_groups()[message['group']]['name']
        elif kind == 'topic-delete':
            message['n_topic'] = message['n_group'] = 'unknown'
        elif kind == 'topic-rename':
            # TODO
            pass
        elif kind in ['login', 'logout']:
            message['n_topic'] = message['n_group'] = ''
        elif kind == 'mention':
            message['n_message'] = message['message']['message']
            message['n_mentioned_user'] = message['mentioned_user']['username']
            message['n_topic'] = message['message']['topic']['name']
            message['n_group'] = \
                self.convore.get_groups()[message['message']['group']]['name']
        elif kind in ['star', 'unstar']:
            message['n_message'] = message['star']['message']['message']
            group, topic = message['star']['message_url'].strip('/').split('/')[:2]
            message['n_topic'] = topic
            message['n_group'] = group
            message['n_starred_user'] = message['star']['message']['user']['username']
        elif kind == 'read':
            message['n_group'] = self.convore.get_groups()[message['group_id']]['name']
            message['n_topic'] = self.convore.get_topic_name(message['topic_id'])
        # TODO:
            # unstar
            # read

        return message
