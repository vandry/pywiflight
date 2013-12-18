#!/usr/bin/python

import wiflight

AnyEtag = object()

class MockClient(object):
    def __init__(self):
        self.contents = {
            'test/foo2': (0, "text/plain", "xxx"),
            'test/foo4': (0, "text/plain", "ccc"),
            'test/foo5': (0, "text/plain", "ddd"),
            'test/foo6': (0, "text/plain", "fff"),
            'a/aircraft/5': (0, "text/xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <aircraft id="5">
                    <tail>C-FFSK</tail>
                    <model>Cessna 172N</model>
                    <cockpit_height>1.5</cockpit_height>
                    <prop_blades>2</prop_blades>
                    <model_url>http://www.wi-flight.net/Cessna_172.kmz</model_url>
                </aircraft>
            """),
            'a/aircraft/62': (0, "text/xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <aircraft id="62">
                    <tail>C-XXXX</tail>
                </aircraft>
            """),
            'a/aircraft/63': (0, "text/xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <aircraft id="63">
                    <tail>C-YYYY</tail>
                </aircraft>
            """),
            'a/flight/3189/': (0, "text/xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <flight id="3189">
                    <start>20100626T233633Z</start>
                    <length>7205.25</length>
                    <master_ontime>7204.0</master_ontime>
                    <engine_ontime>7139.5</engine_ontime>
                    <airtime>6606.75</airtime>
                    <alt_min>134.072</alt_min>
                    <alt_max>887.285</alt_max>
                    <agl_min>-0.182</agl_min>
                    <agl_max>880.297</agl_max>
                    <groundlevel_min>-17.427</groundlevel_min>
                    <groundlevel_max>412.881</groundlevel_max>
                    <gs_max>61.218</gs_max>
                    <vs_min>-5.697</vs_min>
                    <vs_max>6.343</vs_max>
                    <az_min>0.0509114583333</az_min>
                    <az_max>1.62018229167</az_max>
                    <aircraft id="5">
                        <tail>C-FFSK</tail>
                        <model>Cessna 172N</model>
                        <cockpit_height>1.5</cockpit_height>
                        <prop_blades>2</prop_blades>
                        <model_url>http://www.wi-flight.net/Cessna_172.kmz</model_url>
                    </aircraft>
                    <crew/>
                    <headline>local at SWF</headline>
                    <events>
                        <event detected="1" end_time="20100626T234318Z" seq="1" severity="10" start_time="20100626T234318Z" type="takeoff">
                            <runway>09</runway>
                            <airport>SWF</airport>
                            <annotations/>
                        </event>
                        <event detected="1" end_time="20100627T012627Z" seq="2" severity="40" start_time="20100627T012537Z" type="airspace">
                            <designation>5206      </designation>
                            <multiple_code> </multiple_code>
                            <name>R-5206                        </name>
                            <restrictive_type>R</restrictive_type>
                            <annotations/>
                        </event>
                        <event detected="1" end_time="20100627T012629Z" seq="3" severity="40" start_time="20100627T012537Z" type="airspace">
                            <designation>5206      </designation>
                            <multiple_code>A</multiple_code>
                            <name>R-5206                        </name>
                            <restrictive_type>R</restrictive_type>
                            <annotations/>
                        </event>
                        <event detected="1" end_time="20100627T013348Z" seq="4" severity="10" start_time="20100627T013348Z" type="landing">
                            <runway>09</runway>
                            <airport>SWF</airport>
                            <annotations/>
                        </event>
                    </events>
                    <weather t="0.0" windeast="-4.83419648249" windnorth="-1.75950362622">KSWF 262245Z 07010KT 10SM OVC090 24/15 A2986</weather>
                    <weather t="853.5"/>
                    <weather t="1390.0" windeast="-0.267997020866" windnorth="-1.51988663215">KHPN 262256Z 01003KT 10SM SCT090 BKN100 26/16 A2983 RMK AO2 SLP095 T02610156 $</weather>
                    <weather t="1714.75"/>
                    <weather t="1747.25" windeast="2.22760978862" windnorth="-1.28611111111">KTEB 262251Z 30005KT 10SM CLR 29/14 A2980 RMK AO2 DZB24E46 SLP090 P0000 T02890139</weather>
                    <weather t="2280.25" windeast="-0.446661701443" windnorth="-2.53314438691">KEWR 262351Z 01005KT 10SM SCT048 BKN070 BKN140 BKN250 29/13 A2981 RMK AO2 RAE30 SLP095 P0000 60000 T02940133 10339 20294 56005 $</weather>
                    <weather t="2749.5" windeast="3.11865370407" windnorth="1.80055555556">KLGA 262351Z 24007KT 10SM FEW075 BKN120 OVC200 30/14 A2981 RMK AO2 RAB01E27 SLP095 P0000 60000 T03000144 10328 20289 56003</weather>
                    <weather t="2815.0" windeast="2.22760978862" windnorth="-1.28611111111">KTEB 262251Z 30005KT 10SM CLR 29/14 A2980 RMK AO2 DZB24E46 SLP090 P0000 T02890139</weather>
                    <weather t="2901.5" windeast="3.11865370407" windnorth="1.80055555556">KLGA 262351Z 24007KT 10SM FEW075 BKN120 OVC200 30/14 A2981 RMK AO2 RAB01E27 SLP095 P0000 60000 T03000144 10328 20289 56003</weather>
                    <weather t="3185.75" windeast="-0.446661701443" windnorth="-2.53314438691">KEWR 262351Z 01005KT 10SM SCT048 BKN070 BKN140 BKN250 29/13 A2981 RMK AO2 RAE30 SLP095 P0000 60000 T02940133 10339 20294 56005 $</weather>
                    <weather t="3345.75" windeast="3.11865370407" windnorth="1.80055555556">KLGA 262351Z 24007KT 10SM FEW075 BKN120 OVC200 30/14 A2981 RMK AO2 RAB01E27 SLP095 P0000 60000 T03000144 10328 20289 56003</weather>
                    <weather t="3590.75" windeast="2.22760978862" windnorth="-1.28611111111">KTEB 262251Z 30005KT 10SM CLR 29/14 A2980 RMK AO2 DZB24E46 SLP090 P0000 T02890139</weather>
                    <weather t="4201.5" windeast="-0.446661701443" windnorth="-2.53314438691">KEWR 262351Z 01005KT 10SM SCT048 BKN070 BKN140 BKN250 29/13 A2981 RMK AO2 RAE30 SLP095 P0000 60000 T02940133 10339 20294 56005 $</weather>
                    <weather t="4597.25"/>
                    <weather t="4774.25" windeast="-0.446661701443" windnorth="-2.53314438691">KEWR 262351Z 01005KT 10SM SCT048 BKN070 BKN140 BKN250 29/13 A2981 RMK AO2 RAE30 SLP095 P0000 60000 T02940133 10339 20294 56005 $</weather>
                    <weather t="5112.0" windeast="3.11865370407" windnorth="1.80055555556">KLGA 262351Z 24007KT 10SM FEW075 BKN120 OVC200 30/14 A2981 RMK AO2 RAB01E27 SLP095 P0000 60000 T03000144 10328 20289 56003</weather>
                    <weather t="5149.0" windeast="2.22760978862" windnorth="-1.28611111111">KTEB 262251Z 30005KT 10SM CLR 29/14 A2980 RMK AO2 DZB24E46 SLP090 P0000 T02890139</weather>
                    <weather t="5306.5" windeast="3.11865370407" windnorth="1.80055555556">KLGA 262351Z 24007KT 10SM FEW075 BKN120 OVC200 30/14 A2981 RMK AO2 RAB01E27 SLP095 P0000 60000 T03000144 10328 20289 56003</weather>
                    <weather t="5326.0" windeast="2.22760978862" windnorth="-1.28611111111">KTEB 262251Z 30005KT 10SM CLR 29/14 A2980 RMK AO2 DZB24E46 SLP090 P0000 T02890139</weather>
                    <weather t="5670.75"/>
                    <weather t="5704.75" windeast="-0.267997020866" windnorth="-1.51988663215">KHPN 262256Z 01003KT 10SM SCT090 BKN100 26/16 A2983 RMK AO2 SLP095 T02610156 $</weather>
                    <weather t="6100.5"/>
                    <weather t="6548.75" windeast="-4.83419648249" windnorth="-1.75950362622">KSWF 262245Z 07010KT 10SM OVC090 24/15 A2986</weather>
                    <member_of group_name="Demo flights"/>
                    <member_of group_name="Featured flights"/>
                </flight>
            """),
            'a/flight/62/': (0, "text/xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <flight id="62">
                    <crew>
                        <user name="foo"/>
                    </crew>
                </flight>
            """),
            'a/flight/63/': (0, "text/xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <flight id="63">
                    <aircraft id="5">
                        <tail>C-FFSK</tail>
                        <model>Cessna 172N</model>
                        <cockpit_height>1.5</cockpit_height>
                        <prop_blades>2</prop_blades>
                        <model_url>http://www.wi-flight.net/Cessna_172.kmz</model_url>
                    </aircraft>
                </flight>
            """),
            'a/reservation/resv1': (0, "text/xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <reservation domain="dom1" name="resv1">
                    <aircraft id="5">
                        <tail>C-FFSK</tail>
                        <model>Cessna 172N</model>
                        <cockpit_height>1.5</cockpit_height>
                        <prop_blades>2</prop_blades>
                        <model_url>http://www.wi-flight.net/Cessna_172.kmz</model_url>
                    </aircraft>
                    <start>20131201T120000Z</start>
                    <end>20131201T130000Z</end>
                    <notify_profile>placeholder</notify_profile>
                    <crew>
                        <user name="crew1"/>
                        <user name="crew2"/>
                    </crew>
                </reservation>
            """),
            'a/aircraft/?search=filter+words+n%26%26d+encoding': (0, "text/xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <list>
                    <aircraft id="5">
                        <tail>C-FFSK</tail>
                        <model>Cessna 172N</model>
                        <cockpit_height>1.5</cockpit_height>
                        <prop_blades>2</prop_blades>
                        <model_url>http://www.wi-flight.net/Cessna_172.kmz</model_url>
                    </aircraft>
                    <aircraft id="6">
                        <tail>C-FFSL</tail>
                        <model>Cessna 172O</model>
                        <cockpit_height>1.6</cockpit_height>
                        <prop_blades>3</prop_blades>
                        <model_url>http://www.wi-flight.net/Cessna_173.kmz</model_url>
                    </aircraft>
                </list>
            """),
            'a/flight/?kw=123': (0, "text/xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <list>
                    <flight id="1">
                        <headline>1</headline>
                    </flight>
                    <flight id="2">
                        <headline>2</headline>
                    </flight>
                </list>
            """),
            'a/aircraft/65/image': (0, "image/png",
                # 1x1 white
                '\x89PNG\r\n\x1a\n\0\0\0\rIHDR\0\0\0\1\0\0\0\1\1\0\0\0\x007n\xf9$\0\0\0\nIDAT\x08\x99ch\0\0\0\x82\0\x81\xcb\x13\xb2a\0\0\0\0IEND\xaeB`\x82'
            ),
            'a/flight/67/track': (0, "text/xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <flight length="3600.0" start="20131201T000000Z">
                    <point
                        agl="4175.909"
                        alt="4306.879"
                        az="0.796614583333"
                        gs="82.105"
                        head="0.562261150079"
                        lat="50.8325239364"
                        lon="-3.1916370336"
                        rpm="3053"
                        t="900.0"
                        vs="3.742"
                    />
                </flight>
            """),
            'a/crewdb/user%40example.com/fleet1': (0, "text/xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <user>
                    <username>user@example.com</username>
                    <email>user@example.com</email>
                    <name>Kim Vandry</name>
                    <phone>+1 514 907-0802</phone>
                    <dbdomain>fleet1-domain.example.com</dbdomain>
                    <fleet>fleet1</fleet>
                    <signup_done/>
                </user>
            """),
            'a/crewdb?q=example': (0, "text/xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <crewdb_search>
                    <user>
                        <username>user@example.com</username>
                        <email>user@example.com</email>
                        <name>Kim Vandry</name>
                        <phone>+1 514 907-0802</phone>
                        <dbdomain>fleet1-domain.example.com</dbdomain>
                        <fleet>fleet1</fleet>
                        <signup_done/>
                    </user>
                    <fleet dbdomain="fleet1-domain.example.com" name="fleet1"/>
                </crewdb_search>
            """),
            'a/crewdb/user%40example.com': (0, "text/xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <list>
                    <user>
                        <username>user@example.com</username>
                        <email>user@example.com</email>
                        <name>Kim Vandry</name>
                        <phone>+1 514 907-0802</phone>
                        <dbdomain>fleet1-domain.example.com</dbdomain>
                        <fleet>fleet1</fleet>
                        <signup_done/>
                    </user>
                </list>
            """),
            'test/foo%C3%A9%2F%09done': (0, "text/plain", "exists"),
        }

    def request(self, url, method, data=None, content_type="text/xml", etag=AnyEtag):
        if method == 'GET':
            if url in self.contents:
                d = self.contents[url]
                return d[1], d[0], d[2]
            else:
                raise wiflight.HTTPError(url, 404, 'Not found')
        elif method == 'PUT':
            if url in self.contents:
                d = self.contents[url]
                old_etag = d[0]
            else:
                old_etag = None
            if etag is not AnyEtag:
                if etag != old_etag:
                    raise wiflight.HTTPError(url, 412, "ETag mismatch")
            if old_etag is None:
                etag = 0
            else:
                etag = old_etag + 1
            self.contents[url] = etag, content_type, data
        elif method == 'DELETE':
            if url in self.contents:
                d = self.contents[url]
                old_etag = d[0]
            else:
                old_etag = None
            if etag is not AnyEtag:
                if etag != old_etag:
                    raise wiflight.HTTPError(url, 412, "ETag mismatch")
            del self.contents[url]
        else:
            raise wiflight.HTTPError(url, 405, 'Method not allowed')
