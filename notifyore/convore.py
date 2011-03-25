from convoread.convore import Convore
from convoread.utils import debug, error, get_passwd, synchronized

class EnhancedConvore(Convore):

    def __init__(self):
        super(EnhancedConvore, self).__init__()
        self.topic_lookup = {}
        # {group-slug:
        #   {last_until_id:0,
        #   topics: {
        #       'slug':id,
        #       slug:id...}

    def get_group_id(self, group_slug):
        for group_id, group_data in self.get_groups().items():
            if group_data['slug'] == group_slug.lower():
                return group_id

    def topics_by_slug(self, topics):
        indexed_topics = {}
        for topic in topics:
            indexed_topics[topic['slug']] = topic
        return indexed_topics

    def topics_by_id(self, topics):
        indexed_topics = {}
        for topic in topics:
            indexed_topics[topic['id']] = topic
        return indexed_topics

    def get_topic_id(self, topic_url):
        group, topic = topic_url.strip('/').split('/')
        group_id = self.get_group_id(group)
        if not group in self.topic_lookup:
            last_id, topics = self.get_group_topics_batch(group_id)
            # topics contains a simple dictionary of slug:id
            # print topics
            topics_slug_indexed = self.topics_by_slug(topics)
            topics_id_indexed = self.topics_by_id(topics)

            # TODO - the above is not all wrong - and maybe not needed
            # topics_by_slug = topics
            self.topic_lookup[group] = {'last_until_id':last_id, 'topic_by_slug':topics_slug_indexed}
            self.topic_lookup[group]['topic_by_id'] = topics_id_indexed

            # print self.topic_lookup[group]
        found = False
        while not found:
            if topic in self.topic_lookup[group]['topic_by_slug']:
                return self.topic_lookup[group]['topic_by_slug'][topic]['id']
            elif self.topic_lookup[group]['last_until_id']:
                last_id, topics = self.get_group_topics_batch(group_id, self.topic_lookup[group]['last_until_id'])
                topics_slug_indexed = self.topics_by_slug(topics)
                topics_id_indexed = self.topics_by_id(topics)
                self.topic_lookup[group]['last_until_id'] = last_id
                self.topic_lookup[group]['topic_by_slug'].update(topics_slug_indexed)
                self.topic_lookup[group]['topic_by_id'].update(topics_id_indexed)
            else:
                return False

    def get_topic_name(self, topic_id):
        # give the cached data a shot, otherwise hit the API again
        for group in self.topic_lookup:
            if topic_id in self.topic_lookup[group]['topic_by_id']:
                return self.topic_lookup[group]['topic_by_id'][topic_id]['name']
        topic = self.get_topic(topic_id)
        # could stick the topic in the cache at this point
        return topic.get('name','(unknown topic)')

    @synchronized
    def get_topic(self, topic_id):
        url = '/api/topics/{0}.json'.format(topic_id)
        topic = self._connection.request('GET', url).get('topic',{})
        return topic

    @synchronized
    def get_group_topics_batch(self, group_id, until_id=None):
        result = {}
        url = '/api/groups/{0}/topics.json'.format(group_id)
        if until_id:
            url += ('?until_id=' + until_id)

        response = self._connection.request('GET', url)
        # for topic in response.get('topics', []):
            # result[topic['slug']] = topic['id']
        result = response.get('topics', [])

        return (response.get('until_id'), result)

