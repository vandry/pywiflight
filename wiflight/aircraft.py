#!/usr/bin/python

from wiflight.object import APIObject

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
