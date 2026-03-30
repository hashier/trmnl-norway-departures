import responses
import requests
from freezegun import freeze_time

from trmnl import get_live_data_from_ruter

ENTUR_URL = "https://api.entur.io/journey-planner/v3/graphql"


class TestGetLiveDataFromRuter:
    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_successful_response(self, sample_entur_api_response):
        responses.post(ENTUR_URL, json=sample_entur_api_response)

        station_name, data = get_live_data_from_ruter(
            entur_stop="NSR:StopPlace:58366"
        )

        assert station_name == "Jernbanetorget"
        assert len(data) == 4

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_returns_departure_items(self, sample_entur_api_response):
        responses.post(ENTUR_URL, json=sample_entur_api_response)

        _, data = get_live_data_from_ruter()

        first = data[0]
        assert "destinationDisplay" in first
        assert "expectedDepartureTime" in first
        assert "serviceJourney" in first

    @responses.activate
    def test_json_parse_error_returns_error_tuple(self):
        responses.post(ENTUR_URL, body="not json", status=200)

        station_name, data = get_live_data_from_ruter()

        assert "Error" in station_name
        assert data == []

    @responses.activate
    def test_network_error(self):
        responses.post(
            ENTUR_URL, body=requests.ConnectionError("Connection refused")
        )

        try:
            get_live_data_from_ruter()
            assert False, "Should have raised ConnectionError"
        except requests.ConnectionError:
            pass  # Expected — no error handling in current code

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_ignore_departures_within_minutes(self, sample_entur_api_response):
        """Verify the start_time is offset when ignore_departures_within_the_next_minutes is set."""
        responses.post(ENTUR_URL, json=sample_entur_api_response)

        get_live_data_from_ruter(ignore_departures_within_the_next_minutes=15)

        # The GraphQL query should contain a start time 15 minutes after "now"
        sent_body = responses.calls[0].request.body.decode()
        assert "12:15:00" in sent_body
