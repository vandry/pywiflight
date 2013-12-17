#!/usr/bin/python

from wiflight.object import APIObject, APIListObject
from copy import deepcopy
import urllib

class APIAircraft(APIObject):
    """Represents a Wi-Flight aircraft."""
    __slots__ = ()
    _toptag = 'aircraft'

    def __init__(self, aircraft_id):
        """Aircraft may be referenced either by numeric ID or by tail
        number. The numeric ID should be used if available since it
        is the primary key and cannot be changed. However, new aircraft
        can only be referenced by tail number (as an ID does not yet
        exist for them).

        If :param aircraft_id: is a string, the aircraft will be
        referenced by tail number. Otherwise it will be referenced by
        numeric ID.
        """
        if isinstance(aircraft_id, basestring):
            APIObject.__init__(self, "a/aircraft/tail/%s" % (aircraft_id,))
        else:
            APIObject.__init__(self, "a/aircraft/%d" % (aircraft_id,))
            self.body.set('id', str(aircraft_id))

    @classmethod
    def from_xml(cls, xml):
        """Return a new APIAircraft object pre-populated with content

        :param xml: should be an etree <aircraft> tag with optional children.
        It will be copied.

        If the identification of the aircraft cannot be found from the
        aircraft tag, None is returned.
        """
        aircraft_id = xml.get('id')
        if aircraft_id is None:
            tail = xml.get('tail')
            if tail is None:
                return None
            else:
                o = cls(tail)
        else:
            try:
                o = cls(int(aircraft_id))
            except (ValueError, TypeError), e:
                return None
        o.body = deepcopy(xml)
        return o

    @property
    def image(self):
        """Image (PNG, JPEG, etc...) for this aircraft"""
        return APIAircraftImage(self)

for k, v in {
    'tail': "Tail number (identification) of aircraft",
    'model': "Model name of aircraft",
    'model_url': "URL of 3D model which can be used in flight playback",
}.iteritems():
    APIAircraft._add_simple_text_property(k, v)
for k, v in {
    'cockpit_height': "Height of cockpit (or GPS antenna) above ground in metres",
    'prop_blades': "Number of propeller blades",
}.iteritems():
    APIAircraft._add_simple_float_property(k, v)
APIAircraft._add_simple_bool_property(
    'pressurized', 'Flags indicating if aircraft is pressurized'
)
del k, v

class WithAircraftMixIn(object):
    """For objects that have an attached aircraft"""
    __slots__ = ()

    @property
    def aircraft(self):
        """Aircraft associated with this object, as an APIAircraft

        On flights and reservations, the server will accept an <aircraft>
        that is almost empty (only contains an ID or tail number to
        identify the aircraft), so it it not necessary to load the aircraft
        or otherwise populate its attributes (model, prop_blades, etc...).
        Instead, code such as this example is enough:

        reservation.aircraft = wiflight.APIAircraft("C-ABCD")
        reservation.save(client)

        When these objects are returned by the server, however, all of the
        aircraft's attrributes will be filled in.
        """
        aclist = self.body.xpath("/" + self._toptag + "/aircraft")
        if not aclist:
            return None
        ac = aclist[0]
        return APIAircraft.from_xml(aclist[0])

    @aircraft.setter
    def aircraft(self, value):
        if not isinstance(value, APIAircraft):
            raise ValueError("aircraft must be set to APIAircraft object")
        aclist = self.body.xpath("/" + self._toptag + "/aircraft")
        if aclist:
            tag = aclist[0]
            toptag = tag.getparent()
            position = toptag.index(tag)
            for x in aclist:
                x.getparent().remove(x)
            toptag.insert(position, deepcopy(value.body))
        else:
            toptag = self.body.xpath("/" + self._toptag)[0]
            toptag.append(deepcopy(value.body))

    @aircraft.deleter
    def aircraft(self):
        aclist = self.body.xpath("/" + self._toptag + "/aircraft")
        for x in aclist:
            x.getparent().remove(x)

class APIAircraftSearch(APIListObject):
    """Represents a Wi-Flight aircraft search.

    Example:

    # client is an authenticated session (see wiflight.APISession)
    search = wiflight.APIAircraftSearch("C-FRUN")
    search.load(client)
    for aircraft in search:
        pass

    This type of object can only be loaded, not saved or deleted.
    """
    __slots__ = ()
    _toptag = 'list'
    _list_contents_map = { 'aircraft': APIAircraft }

    def __init__(self, query):
        """Search for aircraft by keyword on the server.

        :param query: should be a keyword search string. It is
        direcrlt interpreted by the server. If None, all aircraft
        for which the client has permission will be returned.
        """
        if query is None:
            APIObject.__init__(self, "a/aircraft/")
        else:
            APIObject.__init__(self, "a/aircraft/?" + urllib.urlencode({
                'search': query
            }))

class APIAircraftImage(APIObject):
    """Wi-Flight aircraft image.

    The Content-Type and image data can be get and set through
    the content_type and body properties, respectively.

    Instances of APIAircraftImage should be obtained through
    APIAircraft as follows:

    ac = wiflight.APIAircraft("C-XYZW")
    image = ac.image
    """
    __slots__ = ()

    def __init__(self, api_aircraft):
        """Produce aircraft image given aircraft instance"""
        if not isinstance(api_aircraft, APIAircraft):
            raise TypeError("APIAircraftImage only works on APIAircraft")
        APIObject.__init__(self, api_aircraft.url + "/image")
