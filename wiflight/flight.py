#!/usr/bin/python

from wiflight.object import APIObject
from wiflight.aircraft import WithAircraftMixIn
import lxml.etree

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

    @property
    def crew(self):
        """Set of usernames of crew members who were on this flight

        This is a derived read-only attribute. The server does not
        actually track crew members on flights themselves. Crew members
        appear on flights if they appear in the crew list of any
        reservation that matches the flight.
        """
        return _FlightCrewSet(self.body)

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
