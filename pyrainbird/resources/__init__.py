import json

from pkg_resources import resource_string

# parameters in number of nibbles (based on string representations of SIP bytes), total lengths in number of SIP bytes

# Changed in json version 3.9: The keyword argument encoding has been removed.
# https://docs.python.org/3/library/json.html
_sip_messages = json.loads(resource_string(__name__, 'sip_messages.json').decode("UTF-8"))
requests = _sip_messages["requests"]
responses = _sip_messages["responses"]