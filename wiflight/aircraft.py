#!/usr/bin/python

from wiflight.object import APIObject
from copy import deepcopy

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
            APIObject.__init__(self, "a/aircraft/%d/" % (aircraft_id,))
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
