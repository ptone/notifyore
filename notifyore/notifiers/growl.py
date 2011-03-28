import hashlib
import os
import time
import urllib2
import tempfile

import Growl

from notifyore.notifiers import BaseNotifier
from notifyore.utils import get_convore_logo

def get_growl_image(url):
    cache_folder = os.path.join(tempfile.gettempdir(),'profile image cache')
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)
    fname = '%s.%s' % (hashlib.md5(url).hexdigest(), url.split('.')[-1])
    cached_image = os.path.join(cache_folder,fname)
    image = None
    if os.path.exists(cached_image):
        mtime = os.path.getmtime(cached_image)
        #invalidate if over 3 days old
        if (time.time() - mtime) > (60 * 60 * 24 * 3):
            os.remove(cached_image)
        else:
            image = Growl.Image.imageFromPath(cached_image)
    else:
        f = open(cached_image,'wb')
        f.write(urllib2.urlopen(url).read())
        f.close()
        image = Growl.Image.imageFromPath(cached_image)
    return image

class GrowlNotifier(BaseNotifier):
    def __init__(self, *args, **kwargs):
        self.notification_name = kwargs.pop('name', 'Convore Notification')
        super(GrowlNotifier, self).__init__(*args, **kwargs)
        self.default_image = Growl.Image.imageFromPath(get_convore_logo())
        self.growl = Growl.GrowlNotifier(kwargs.get('appname', 'Notifyore'),
                [self.notification_name], applicationIcon = self.default_image)
        self.growl.register()

    def handle_message(self, message):
        # growl notification requires:
        # title
        # text
        # img (optional)
        # sticky flag
        message = self.normalize_message(message)

        if 'user' in message:
            img = get_growl_image(message['user']['img'])
            icon = img

        kind = message['kind']
        description = message.get('n_message', '')
        if description == '':
            description = kind
        title = None
        group = message['n_group']
        topic = message['n_topic']
        user_line = message['n_user']
        title_template = """%(group)s
 %(topic)s
  %(user_line)s"""

        # should display message as:
        # Group
        #  Topic
        #   Author
        # Body of message
        if kind == 'mention':
            # notification_args['title'] = "%s mentioned you" % notification_args['title']
            user_line = "%s mentioned you" % message['n_user']
        elif kind == 'topic':
            title = "%s created a new topic\nin %s" % (message['n_user'], message['n_group'])
            description = message['n_topic']
        elif kind in ['login','logout']:
            description = kind
        elif kind in ['star', 'unstar']:
            user_line = "{user} {kind}red message".format(
                user=user_line,
                kind=kind)
        if not title:
            title = title_template % {
                    'group':group,
                    'topic':topic,
                    'user_line':user_line}
        self.growl.notify(
                self.notification_name,
                title,
                description,
                icon=icon)

