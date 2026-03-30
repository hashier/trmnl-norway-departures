import json
from unittest.mock import MagicMock, patch

import responses
from freezegun import freeze_time

from trmnl import http

ENTUR_URL = "https://api.entur.io/journey-planner/v3/graphql"


def make_request(args=None):
    """Create a mock Flask request with the given query args."""
    request = MagicMock()
    request.args = args or {}
    request.get_json.return_value = None
    return request


class TestHttpHandler:
    def test_missing_secret_returns_403(self):
        request = make_request({})
        body, status, headers = http(request)

        assert status == 403
        assert body == "denied"

    def test_wrong_secret_returns_403(self):
        request = make_request({"secret": "wrong"})
        body, status, headers = http(request)

        assert status == 403

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_valid_request_returns_200(self, sample_entur_api_response):
        responses.post(ENTUR_URL, json=sample_entur_api_response)
        request = make_request({"secret": "public"})

        body, status, headers = http(request)

        assert status == 200
        parsed = json.loads(body)
        assert "departures" in parsed

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_custom_stop_parameter(self, sample_entur_api_response):
        responses.post(ENTUR_URL, json=sample_entur_api_response)
        request = make_request(
            {"secret": "public", "stop": "NSR:StopPlace:59872"}
        )

        body, status, _ = http(request)

        assert status == 200
        # Verify the stop was passed through to the API
        sent_body = responses.calls[0].request.body.decode()
        assert "NSR:StopPlace:59872" in sent_body

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_exclude_platforms_parameter(self, sample_entur_api_response):
        responses.post(ENTUR_URL, json=sample_entur_api_response)
        request = make_request(
            {"secret": "public", "exclude_platforms": "A,B"}
        )

        body, status, _ = http(request)

        assert status == 200
        parsed = json.loads(body)
        assert parsed["exclude_platforms"] == "A,B"

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_default_stop_when_empty(self, sample_entur_api_response):
        responses.post(ENTUR_URL, json=sample_entur_api_response)
        # stop param present but empty
        request = make_request({"secret": "public", "stop": ""})

        http(request)

        sent_body = responses.calls[0].request.body.decode()
        # Should fall back to Jernbanetorget
        assert "NSR:StopPlace:58366" in sent_body

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_response_headers(self, sample_entur_api_response):
        responses.post(ENTUR_URL, json=sample_entur_api_response)
        request = make_request({"secret": "public"})

        _, _, headers = http(request)

        assert "Content-Type" in headers
        assert "application/json" in headers["Content-Type"]
