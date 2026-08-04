import httpx

from meridian.ingest.air_quality import fetch_amsterdam_stations

FALSE_POSITIVE_NUMBER = "NL_REPLACE_ME"
FALSE_POSITIVE_LOCATION = "REPLACE_ME"
FALSE_POSITIVE_MUNICIPALITY = "REPLACE_ME"


def test_excludes_amsterdamse_false_positive():
    stations_page = {
        "pagination": {"current_page": 1, "last_page": 1},
        "data": [
            {"number": "NL_REAL", "location": "Amsterdam Vondelpark"},
            {"number": FALSE_POSITIVE_NUMBER, "location": FALSE_POSITIVE_LOCATION},
        ],
    }
    details = {
        "NL_REAL": {"number": "NL_REAL", "location": "Amsterdam Vondelpark", "municipality": "Amsterdam", "geometry": {"coordinates": [4.8686, 52.3579]}},
        FALSE_POSITIVE_NUMBER: {
            "number": FALSE_POSITIVE_NUMBER,
            "location": FALSE_POSITIVE_LOCATION,
            "municipality": FALSE_POSITIVE_MUNICIPALITY,
            "geometry": {"coordinates": [4.9, 52.1]},
        },
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/open_api/stations":
            return httpx.Response(200, json=stations_page)
        number = request.url.path.rsplit("/", 1)[-1]
        return httpx.Response(200, json={"data": details[number]})

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.luchtmeetnet.nl/open_api")
    confirmed = fetch_amsterdam_stations(client)
    assert set(confirmed["station_number"]) == {"NL_REAL"}
