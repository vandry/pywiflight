#!/usr/bin/python

from wiflight.object import APIObject
from wiflight.aircraft import WithAircraftMixIn
import lxml.etree

class _ResvCrewSet(object):
    __slots__ = ('doc',)

    def __init__(self, doc):
        self.doc = doc

    def __iter__(self):
        return iter(self.doc.xpath("/reservation/crew/user/@name"))

    def __repr__(self):
        return repr(set(self))

    def add(self, username):
        if username not in self:
            toptag = self.doc.xpath("/reservation/crew")[0]
            tag = lxml.etree.Element('user')
            tag.set('name', username)
            toptag.append(tag)

    def remove(self, username):
        for tag in self.doc.xpath("/reservation/crew/user"):
            if tag.get('name') == username:
                tag.getparent().remove(tag)

class APIReservation(APIObject, WithAircraftMixIn):
    """Represents a Wi-Flight reservation.

    Reservations are used to inform the system of which airplanes are
    scheduled to be flying, when they are scheduled to fly, and who is
    aboard. Reservations are usually created before the airplane flies,
    but they can also be created retrospectively.

    Whenever reservations are created or updated, the system checks to
    see if the reservation can be matched against any outstanding
    flights. Similarily, whenever a new flight is registered, the system
    checks to see if it can be matched with a previously created
    reservation. When a match is found, the flight is associated with
    the reservation, which has the following consequences:

    - The crew listed on the reservation record will be added to the
    flight's crew, which can enable the crew to have access to the
    flight.
    - If there is a callback registered on the reservation, the flight
    details will be forwarded to an external system (such as a flight
    reservation and dispatch sytstem).
    - Flight analysis may take into account the crew's level of
    training and certification (future functionality).
    """

    __slots__ = ()
    _toptag = 'reservation'

    def __init__(self, reservation_name):
        APIObject.__init__(self, 'a', 'reservation', reservation_name)
        self.body.set('name', reservation_name)

    @property
    def name(self):
        """Name of this reservation. Each reservation must have a unique name."""
        return self.body.get('name')

    @property
    def domain(self):
        """The domain of a reservation marks which collection is is part of

        The domain is an arbitrary string. Reservations in the same
        domain will compete with each other to match flights. Only the
        best-matching reservation in each domain will match a flight.
        (On the other hand, a single reservation may match any number
        of flights, especially if its time bounds are very wide.)

        If different external systems integrate with Wi-Flight operating
        on the same set of aircraft (for example, a dispatch system plus
        a maintenance system), they should use reservations with different
        domains.
        """
        return self.body.get('domain')

    @domain.setter
    def domain(self, value):
        self.body.set('domain', value)

    @property
    def crew(self):
        """Set of usernames of crew members associated with this reservation"""
        return _ResvCrewSet(self.body)

APIReservation._add_simple_date_property('start', 'Start bound of reservation in UTC')
APIReservation._add_simple_date_property('end', 'End bound of reservation in UTC')
APIReservation._add_simple_text_property(
    'notify_profile',
    """Specifies how an external system should be notified
    whenever this reservation matches a flight. Set to a
    string value that names an algorithm that has been
    preregistered with the Wi-Flight server."""
)
