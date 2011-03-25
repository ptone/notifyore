import re
import time


class Rule(object):
    """
    object that stores a rule determining whether a convore live event
    should be acted on, and how
    """
    def message_for_match(self, orig_message):
        """
        Normalizes some of the message data to make it easier to test the rule

        want to make the following consistently available:

        user: username of person creating action
        topic: id of topic
        group: group id
        """
        # make a shallow copy to use and keep original to hand off to notifiers
        message = orig_message.copy()
        kind = message['kind']
        # simplify data so that it is easier to match
        if 'user' in message:
            message['user'] = message['user']['username']
        if kind == 'message':
            message['topic_id'] = message['topic']['id']
            # group is already group id
        elif kind == 'topic':
            message['user'] = message['creator']['username']
            message['topic'] = message['id']
        elif kind == 'mention':
            message['message'] = message['message']['message']
            # currently only receive mentions for yourself, but thinking ahead:
            message['mentioned_user'] = message['mentioned_user']['username']
        elif kind in ['star', 'unstar']:
            message['starred_user'] = message['star']['message']['user']['username']
            message['message'] = message['star']['message']['message']
            message_url = message['star']['message_url'].strip('/')
            message_url = '/'.join(message_url.split('/')[:2])
            message['topic'] = self.convore.get_topic_id(message_url)
            message['group'] = self.convore.get_group_id(message_url.split('/')[0])
        return message

    def __init__(self, convore, *args, **kwargs):
        self.convore = convore
        self.match_events = kwargs.get('match_events', [])
        self.exclude_events = kwargs.get('exclude_events', [])
        self.match_attributes = kwargs.get('match_attributes', {})
        self.exclude_attributes = kwargs.get('exclude_attributes', {})
        self.actions = kwargs.get('actions', [])
        self.last_action = 0
        if self.match_events and self.exclude_events:
            raise ValueError("can only define events to match or exclude, not both")
        if self.match_attributes and self.exclude_attributes:
            raise ValueError("can only define attributes to match or exclude, not both")
        # TODO: verify that attributes make sense:
        #   for example can't filter to group and topic (especially if topic not in that group)

        # TODO support case insensive message search

        self.mention = re.compile("@" + self.convore.get_username(), re.IGNORECASE)


        # TODO:
        # rate_limit_after_count
        # rate_limit_within
        # rate_limit_reset_duration
        # growl_priority
        # time of day limits

        for attrlist in [self.match_attributes, self.exclude_attributes]:
            for key in attrlist:
                if key == 'group':
                    attrlist[key] = self.convore.get_group_id(attrlist[key])
                if key == 'topic':
                    attrlist['topic_id'] = self.convore.get_topic_id(attrlist[key])
                    # @@ not sure this is good if we want to update rules at runtime
                    # if we need to rebuild, can check is topic_slug defined
                    attrlist['topic_slug'] = attrlist['topic']
                    del(attrlist['topic'])

    def handle_message(self, original_message):
        """
        test a message agains the rule, and if a match, perform action(s)
        """
        match_message = self.message_for_match(original_message)
        kind = match_message['kind']

        if ((self.match_events and kind not in self.match_events) or
                (self.exclude_events and kind in self.exclude_events)):
            return False
        if self.match_attributes:
            for key, val in self.match_attributes.items():
                if kind in ['login', 'logout'] and key == 'group':
                    # logouts logins special in that they have a list of group_ids
                    if val not in match_message['group_ids']:
                        return False
                if key in match_message:
                    if not val.lower() == match_message[key].lower():
                        return False
                if key == 'message_search':
                    if 'message' not in match_message:
                        return False
                    if not re.search(val, match_message['message']):
                        return False
        # TODO repeat the above, or factor for exclude attributes

        # print self.match_events
        # print self.match_attributes
        # we have an event to notify for
        for action in self.actions:
            # actions should be instances of a notifier subclass
            self.last_action = time.time()
            action.handle_message(original_message)
        return True


