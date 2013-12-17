#!/usr/bin/python

from wiflight.object import APIObject, APIListObject, _encode_iso8601
from wiflight.aircraft import WithAircraftMixIn
import lxml.etree
from copy import deepcopy
import urllib
import decimal

class _FlightCrewSet(object):
    __slots__ = ('doc',)

    def __init__(self, doc):
        self.doc = doc

    def __iter__(self):
        return iter(self.doc.xpath("/flight/crew/user/@name"))

    def __repr__(self):
        return repr(set(self))

    def add(self, username):
        if username not in self:
            toptag = self.doc.xpath("/flight/crew")[0]
            tag = lxml.etree.Element('user')
            tag.set('name', username)
            toptag.append(tag)

    def remove(self, username):
        for tag in self.doc.xpath("/flight/crew/user"):
            if tag.get('name') == username:
                tag.getparent().remove(tag)

class APIFlight(APIObject, WithAircraftMixIn):
    """Represents a Wi-Flight flight.

    Flights cannot be created through the API. Only incoming data
    from flight data recorders generates flights.

    Most of the data in a flight is derived from the flight recorder
    data and is read-only. Although this class permits modifications
    to all fields, the server will not accept them if they are saved.
    """
    __slots__ = ()
    _toptag = 'flight'

    def __init__(self, flight_id):
        APIObject.__init__(self, "a/flight/%d/" % (flight_id,))
        self.body.set('id', str(flight_id))

    @classmethod
    def from_xml(cls, xml):
        """Return a new APIFlight object pre-populated with content

        :param xml: should be an etree <flight> tag with optional children.
        It will be copied.

        If the identification of the flight cannot be found from the
        flight tag, None is returned.
        """
        try:
            flight_id = int(xml.get('id'))
        except (ValueError, TypeError):
            return None
        o = cls(flight_id)
        o.body = deepcopy(xml)
        return o

    @property
    def crew(self):
        """Set of usernames of crew members who were on this flight

        This is a derived read-only attribute. The server does not
        actually track crew members on flights themselves. Crew members
        appear on flights if they appear in the crew list of any
        reservation that matches the flight.
        """
        return _FlightCrewSet(self.body)

    def track(self, offset=0, length=None):
        """Return an object for querying the time-series flight data

        :param offset: Offset in seconds from start of flight
        :param length: Length in seconds of list to download

        The server limits the length to 10 minutes, so multiple
        queries are almost always necessary to download a whole
        flight.
        """
        return APIFlightTrack(self, offset, length)

    # events and weather not implemented yet!

APIFlight._add_simple_date_property('start', 'Start of flight in UTC')
for k, v in {
    'length': "Length of flight in seconds",
    'master_ontime': "Total amount of time in seconds that power was on",
    'engine_ontime': "Total amount of time in seconds that the engine was on",
    'airtime': "Total amount of time in seconds that aircraft was in the air",
    'alt_min': "Lowest MSL altitude in metres achieved throughout the flight",
    'alt_max': "Highest MSL altitude in metres achieved throughout the flight",
    'agl_min': "Lowest AGL altitude in metres achieved throughout the flight",
    'agl_max': "Highest AGL altitude in metres achieved throughout the flight",
    'groundlevel_min': "Lowest height of ground in metres throughout the flight",
    'groundlevel_max': "Highest height of ground in metres throughout the flight",
    'gs_max': "Highest ground speed in m/s throughout the flight",
    'vs_min': "Lowest vertical speed in m/s throughout the flight",
    'vs_max': "Highest vertical speed in m/s throughout the flight",
    'az_min': "Lowest z-axis acceleration in g throughout the flight",
    'az_max': "Highest z-axis acceleration in g throughout the flight",
}.iteritems():
    APIFlight._add_simple_float_property(k, v)
APIFlight._add_simple_text_property('headline', 'Short text string that describes the flight')
del k, v

class APIFlightSearch(APIListObject):
    """Represents a Wi-Flight flight search.

    Example:

    # client is an authenticated session (see wiflight.APISession)
    search = wiflight.APIFlightSearch(
        # only flights on 2014-02-01
        start=datetime.datetime(2014,2,1,0,0,0),
        end=datetime.datetime(2014,2,2,0,0,0),
        # matching these keywords
        kw="lowlevel"
    )
    search.load(client)
    for flight in search:
        pass

    This type of object can only be loaded, not saved or deleted.
    """
    __slots__ = ()
    _toptag = 'list'
    _list_contents_map = { 'flight': APIFlight }

    def __init__(
        self, kw=None, start=None, end=None, events=None,
        group=[], f=[], missingaircraft=False
    ):
        """Search for flights on the server.

        Only flights matching ALL of the specified criteria are returned.

        :param kw: search keywords. Can be (portions of) aircraft identifier,
        names of events found by analysis, part of the headline, airport
        identifiers, etc...

        :param start: start boundary of the search, in UTC

        :param end: end boundary of the search, in UTC

        :param f: sequence of integer flight IDs. If given, the search will
        be restricted to flights with those IDs

        :param missingaircraft: if True, only flights which are not
        registered to any aircraft will be returned

        :param group: sequence of group names (strings) which the flights
        must be members of

        :param events: if False, None, or not specified, abbreviated flight
        information without events is returned. If True, flights are returned
        including events. Otherwise, a string which is a comma-separated list
        of ranges of event severities to count. The events in each range of
        severities are counted separately and returned in a special
        <event_counts> tag. For example, "30..39,.." (used at the time of
        writing by the Wi-Flight flight browser at
        https://www.wi-flight.net/flight/ ) produces two event counts: one
        count of events with severities between 30 and 39, and the other
        counts all events (unbounded range).
        """
        p = []
        if kw:
            p.append(('kw', kw))
        if start:
            p.append(('start', _encode_iso8601(start)))
        if end:
            p.append(('end', _encode_iso8601(end)))
        if missingaircraft:
            p.append(('missingaircraft', '1'))
        for g in group:
            p.append(('group', g))
        for f1 in f:
            p.append(('f', int(f1)))
        if events is True:
            p.append(('events', 'true'))
        elif events is not False and events is not None:
            p.append(('events', events))
        if p:
            APIObject.__init__(self, "a/flight/?" + urllib.urlencode(p))
        else:
            APIObject.__init__(self, "a/flight/")

def APIFlightTrackPoint():
    attributes = [
        ('t', 'Timestamp in seconds since beginning of flight'),
        ('agl', 'Distance between ground and aircraft in metres'),
        ('alt', 'Distance between geoid and aircraft in metres'),
        ('az', 'z-axis measured acceleration in g'),
        ('gs', 'Ground speed in m/s'),
        ('head', 'Track heading in radians'),
        ('lat', 'Latitude in degrees'),
        ('lon', 'Longitude in degrees'),
        ('rpm', 'Detected engine RPM'),
        ('vs', 'Vertical speed in m/s'),
    ]
    d = { '__slots__': () }
    def _tuple_accessor(idx, doc):
        return property(lambda self: self[idx], doc=doc)
    for n, tpa in enumerate(attributes):
        d[tpa[0]] = _tuple_accessor(n, tpa[1])
    attributes = list(x[0] for x in attributes)
    def from_xml(cls, xml):
        def _get_decimal(name):
            v = xml.get(name)
            if v is None:
                return None
            else:
                return decimal.Decimal(v)
        return cls(_get_decimal(x) for x in attributes)
    d['from_xml'] = classmethod(from_xml)
    return type('APIFlightTrackPoint', (tuple,), d)
APIFlightTrackPoint = APIFlightTrackPoint()

class APIFlightTrack(APIListObject):
    """Object for querying the time-series flight data

    After loading, this object is a sequence of track points containing
    GPS position, accelerometer information, etc...
    """
    __slots__ = ()
    _toptag = 'flight'  # Poor choice, but that's what the server sends
    _list_contents_map = { 'point': APIFlightTrackPoint }

    def __init__(self, api_flight, offset=0, length=None):
        """Initialize query for flight track data.

        :param offset: Offset in seconds from start of flight
        :param length: Length in seconds of list to download

        The server limits the length to 10 minutes, so multiple
        queries are almost always necessary to download a whole
        flight.
        """
        if not isinstance(api_flight, APIFlight):
            raise TypeError("APIFlightTrack only works on APIFlight")
        p = []
        if offset is not None and offset != 0:
            p.append(('offset', str(offset)))
        if length is not None:
            p.append(('length', str(length)))
        if p:
            APIObject.__init__(self, api_flight.url + "track?" + urllib.urlencode(p))
        else:
            APIObject.__init__(self, api_flight.url + "track")
