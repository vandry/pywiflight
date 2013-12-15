wiflight - API client for Wi-Flight (https://www.wi-flight.net)
===============================================================

:Author: Kim Vandry <vandry@TZoNE.ORG>

Introduction
~~~~~~~~~~~~

The wiflight module offers convenient access to Wi-Flight's REST API
from Python. Wi-Flight is an automated solution for aircraft flight data
monitoring which includes a flight data recorder that uploads via wifi,
a server to receive and analyse the flight data, and web applications to
browse recorded flights and play them back. For more information, visit
`our web page <https://www.wi-flight.net>`_.

The Wi-Flight server offers a REST API for accessing various types of
objects such as flights, aircraft, and reservations. All of the
functionality needed for sophisticated applications such as
`the flight browser <https://www.wi-flight.net/flight/>`_ and
`the online flight playback tool <https://www.wi-flight.net/flightview>`_
is available through this API.

The Python interface to the API was created primarily not for use by such
end-user applications as those mentioned above (which are written in
Javascript) although it can be used for this. Its primary purpose is to
facilitate server-to-server communications for integrating Wi-Flight with
reservation and dispatch systems, aircraft maintenance systems, and
the like. Examples of these types of integrations are:

- Reservation systems can populate crew information in Wi-Flight.
  Given crew information, Wi-Flight can offer access to flight playbacks
  restricted to those crew members who were on board and aircraft for
  each particular flight.
- An aircraft maintenance system can receive flight times (e.g. engine
  on time) from Wi-Flight after each flight, enabling it to automatically
  calculate when the aircraft becomes due for regular maintenance.

Usage
~~~~~
