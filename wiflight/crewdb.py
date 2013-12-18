#!/usr/bin/python

"""CrewDb - convenience database on Wi-Flight server

CrewDb is a convenience database maintained on the Wi-Flight server.
Most of the Wi-Flight objects such as flights, aircraft, and
reservations are not related to the CrewDb in any way, and none of
the flight analysis looks at CrewDb. The only link between CrewDb and
Wi-Flight proper is automated signups: inviting a user from a CrewDb
to sign up to Wi-Flight connects the CrewDb entry to a Wi-Flight user.

The CrewDb exists in order to facilitate building a crew management
application on top of Wi-Flight.
"""

from wiflight.object import APIObject, APIListObject
from copy import deepcopy
import urllib

class APICrewDbEntry(APIObject):
    """Represents a single entry in a CrewDb

    CrewDb is a convenience database maintained on the Wi-Flight server.
    Most of the Wi-Flight objects such as flights, aircraft, and
    reservations are not related to the CrewDb in any way, and none
    of the flight analysis looks at CrewDb. The only link between
    CrewDb and Wi-Flight proper is automated signups: inviting a
    user from a CrewDb to sign up to Wi-Flight connects the CrewDb
    entry to a Wi-Flight user.

    The CrewDb exists in order to facilitate building a crew management
    application on top of Wi-Flight.
    """
    __slots__ = ()
    _toptag = 'user'

    def __init__(self, fleetname, username):
        # Note that even though users are contained inside fleets,
        # not the other way around, and URL components are usually
        # expected to be more or less big endian, in this case the
        # username comes first. This is done to make it consistent
        # with the URL a/crewdb/username (no fleet) that searches
        # for a given username in any fleet
        APIObject.__init__(self, 'a', 'crewdb', username, fleetname)
        self.username = username
        self.fleet = fleetname

    @classmethod
    def from_xml(cls, xml):
        """Return a new APICrewDbEntry object pre-populated with content

        :param xml: should be an etree <user> tag with optional children.
        It will be copied.

        If the identification of the CrewDbEntry cannot be found from the
        XML content, None is returned.
        """
        xml = deepcopy(xml)
        username_list = xml.xpath("/user/username/text()")
        fleetname_list = xml.xpath("/user/fleet/text()")
        if not username_list or not fleetname_list:
            return None
        o = cls(''.join(fleetname_list), ''.join(username_list))
        o.body = xml
        return o

for k, v in {
    'username': "Username of this entry (part of the key; normally en email address)",
    'email': "Email address of user (normally matches username)",
    'name': "Display name of user",
    'phone': "Phone number of user",
    'dbdomain': """Domain name associated with the fleet

        Normally, Wi-Flight fleet administrator account's permissions are
        set up so that reservations and users inside those reservations
        with names ending with "@" and this domain are authorized to be
        created in the system. An application using CrewDb should therefore
        use this field to know what suffix in can use for the names of newly
        created reservations and auto-created users.""",
    'fleet': "Name of fleet this CrewDbEntry belongs to (part of the key)",
}.iteritems():
    APICrewDbEntry._add_simple_text_property(k, v)
del k, v
APICrewDbEntry._add_simple_bool_property(
    'signup_done', "True if this user has completed a Wi-Flight signup"
)

class APIFleet(APIObject):
    """Represents a fleet

    Each fleet has its own disjoint set of entries in CrewDb.
    Applications which integrate with Wi-Flight using CrewDb are
    normally each given access to a single fleet.
    """
    __slots__ = ()
    _toptag = 'fleet'

    def __init__(self, fleetname):
        APIObject.__init__(self, 'a', 'fleet', fleetname)
        self.body.set('name', fleetname)

    @classmethod
    def from_xml(cls, xml):
        """Return a new APIFleet object pre-populated with content

        :param xml: should be an etree <fleet> tag with optional children.
        It will be copied.

        If the identification of the aircraft cannot be found from the
        aircraft tag, None is returned.
        """
        fleetname = xml.get('name')
        if fleetname is None:
            return None
        o = cls(fleetname)
        xml = deepcopy(xml)
        o.body = xml
        # Unfortunately, there are two different XML formats for this
        # object. Make it into the canonical format.
        dbdomain = xml.get('dbdomain')
        if dbdomain is not None:
            del xml.attrib['dbdomain']
            o.temporary_username_domain = dbdomain
        return o

    @property
    def name(self):
        """Name (primary key) of this fleet"""
        return self.body.get('name')

APIFleet._add_simple_text_property('description', "Fleet display name")
APIFleet._add_simple_text_property(
    'temporary_username_domain', """
        Normally, Wi-Flight fleet administrator account's permissions are
        set up so that reservations and users inside those reservations
        with names ending with "@" and this domain are authorized to be
        created in the system. An application using CrewDb should therefore
        use this field to know what suffix in can use for the names of newly
        created reservations and auto-created users."""
)

class APICrewDbSearch(APIListObject):
    """Represents a CrewDb search

    CrewDb is a convenience database maintained on the Wi-Flight server.
    Most of the Wi-Flight objects such as flights, aircraft, and
    reservations are not related to the CrewDb in any way, and none
    of the flight analysis looks at CrewDb. The only link between
    CrewDb and Wi-Flight proper is automated signups: inviting a
    user from a CrewDb to sign up to Wi-Flight connects the CrewDb
    entry to a Wi-Flight user.

    The CrewDb exists in order to facilitate building a crew management
    application on top of Wi-Flight.

    This type of object can only be loaded, not saved or deleted.
    """
    __slots__ = ()
    _toptag = 'crewdb_search'
    _list_contents_map = { 'fleet': APIFleet, 'user': APICrewDbEntry }

    def __init__(self, query):
        """Search for CrewDb entries by keyword on the server.

        :param query: should be a keyword search string. It is
        directly interpreted by the server. It is required.
        """
        APIObject.__init__(self, 'a', 'crewdb', query_string=urllib.urlencode({
            'q': query
        }))

class APICrewDbAnyFleet(APIListObject):
    """Use this instead of directly accessing the CrewDbEntry when
    you know its username but you do not know which fleet it is in.
    """
    __slots__ = ()
    _toptag = 'list'
    _list_contents_map = { 'user': APICrewDbEntry }

    def __init__(self, username):
        """Search for CrewDb entries by username on the server.
        """
        APIObject.__init__(self, 'a', 'crewdb', username)
