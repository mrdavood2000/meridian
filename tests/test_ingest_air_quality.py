"""No live network calls in tests - httpx.MockTransport stands in for the
real API so these run offline and deterministically in CI.
"""

import httpx

from meridian.ingest.air_quality import fetch_amsterdam_stations

STATIONS_PAGE = {
    "pagination": {"current_page": 1, "last_page": 1},
    "data": [
        {"number": "NL49022", "location": "Amsterdam-Ookmeer"},
        {"number": "NL10445", "location": "Den Haag-Amsterdamse Veerkade"},
    ],
}

STATION_DETAIL = {
    "NL49022": {
        "data": {
            "location": "Amsterdam-Ookmeer",
            "municipality": "Amsterdam",
            "geometry": {"coordinates": [4.80, 52.38]},
        }
    },
    "NL10445": {
        "data": {
            "location": "Den Haag-Amsterdamse Veerkade",
            "municipality": "'s-Gravenhage",
            "geometry": {"coordinates": [4.31, 52.08]},
        }
    },
}


def test_the_municipality_field_filters_out_a_location_string_false_positive():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/open_api/stations":
            return httpx.Response(200, json=STATIONS_PAGE)
        number = request.url.path.rsplit("/", 1)[-1]
        return httpx.Response(200, json=STATION_DETAIL[number])

    client = httpx.Client(transport=httpx.MockTransport(handler))
    stations = fetch_amsterdam_stations(client=client)

    assert list(stations["station_number"]) == ["NL49022"]
