Noifyore: a notification tool for Convore.com
=============================================

This tool watches the stream of events provided by the Convore API, and
provides a way for you to receive notifications of interest on the Convore
site.

Convore itself provides a very cool "Growl" style popup notice when you get
a mention somewhere else on the site. But if you are on a different page, or in
a different application on your computer, or away entirely - there is no way to
be notified.

Also, while Convore provides a builtin way of getting notified of mentions,
there are plenty of other events that could be of interest.

Notifyore takes the approach of matching an event agaist a list of rules, and
if a match is found, it executes the associated actions.

In english, these would look like:

notify me of mentions in the topic 'cool stuff' with prowl
notify me of messages by user joe34 with growl
notify me of new topics in group 'weather' with growl
notify me of logins of user bob with prowl
notify me of messages by user John in group 'lunch' with prowl and growl
notify me of messages containing "beef" starred by George, written by Sue by
email

etc

Installation
------------

This package currently uses the wrapper embedded in `covoread
<https://github.com/foobarbuzz/convoread>`_ for its access of the Convore API.

Convoread stores your Convore password in your .netrc file - see Convoread's
readme for more inforation.

If you want to use Growl on the Mac, you will need Growl's python bindings
available from `Growl developer site <http://growl.info/documentation/developer/python-support.php
h>`_ or from my `github mirror <https://github.com/ptone/pygrowl>`_.

Configuration and Usage
-----------------------

Notifyore watches your live stream provided by the Convore API.

For each event that occurs, Notifyore will test it against a list of rules, and
if a rule matches, it will pass the event onto one or notfier actions.

A rule may contain the following parts:

match_events: a list of event types this rule will match
exclude_events: a list of event types that if matched, will abort the rule
match_attributes: a dictionary of attributes, all of which must match the event
for the rule to fire.
actions: a list of actions to perform if the rule's conditions are met

The following are not yet supported but planned:

* priority: a priority (that is used by growl and others)
* exclude_attributes: like exclude_events but for attributes
* rate_limit_after_count: number of messages in a burst before this rule is
* paused
* rate_limit_within: time within which the count threshold events must happen
* quiet_period: how long to pause the rule after threshold reached
* time_of_day_limit: only fire during certain hours

Events
~~~~~~

Events are one of:

* message
* message-delete
* topic
* topic-delete
* topic-rename
* login
* logout
* star
* unstar
* read
* mention

Attributes
~~~~~~~~~~

Attributes are one of:

* user: username of person creating action
* topic: url of group-slug/topic-slug for topic
* group: group-slug
* message_search: a string or regex pattern to search for in body of message
* starred_user: the user who wrote the message being starred

Actions
~~~~~~~

Actions are a generally a sublcass of notifyore.notifiers.BaseNotifier

Current builtin actions include:

* raw: print the raw json from the API
* stream: write out a text version of event to a stream (defaults to stdout)
* growl: the MacOs notificatoin utility, with the Prowl iPhone app, these can be
* push notifications to your iPhone

Additional notifier actions can be written and added. Some might include:

* direct Prowl API, to use without growl or a Mac
* email
* sms
* Android C2DM push system
* HTTP POST

Right now at this early stage, the entry point for using the tool is a little
weak. Currently you need to copy and modify the sample watching script included
in the root of the distribution.

TODO:
-----

* Clean up the entry point and configuration
* Potentially move to a attr style access for API data instead of dict
* Add additional notifier backends as noted above
* Add a micro web UI for managing rules
