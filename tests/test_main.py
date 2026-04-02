import json
from unittest.mock import patch

import responses
from freezegun import freeze_time

from trmnl import main

ENTUR_URL = "https://api.entur.io/journey-planner/v3/graphql"


class TestMain:
    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_returns_valid_json(self, sample_entur_api_response):
        responses.post(ENTUR_URL, json=sample_entur_api_response)

        result = main(entur_stop="NSR:StopPlace:58366")
        parsed = json.loads(result)

        assert "departures" in parsed
        assert "name" in parsed
        assert parsed["name"] == "Jernbanetorget"

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_metadata_fields(self, sample_entur_api_response):
        responses.post(ENTUR_URL, json=sample_entur_api_response)

        parsed = json.loads(main())

        assert "last_updated" in parsed
        assert "minutes_to_fetch" in parsed
        assert "num_departures" in parsed
        assert "num_departures-excludes" in parsed

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_platform_exclusion(self, sample_entur_api_response):
        responses.post(ENTUR_URL, json=sample_entur_api_response)

        parsed = json.loads(main(exclude_platforms="A"))

        # FB1A departure on platform "A" should be excluded
        departures = parsed["departures"]
        assert "FB1A" not in departures

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_platform_exclusion_multiple(self, sample_entur_api_response):
        responses.post(ENTUR_URL, json=sample_entur_api_response)

        parsed = json.loads(main(exclude_platforms="A,2"))

        departures = parsed["departures"]
        # Platform A (FB1A) and platform 2 (line 2) should both be excluded
        assert "FB1A" not in departures
        assert 2 not in departures and "2" not in departures

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_platform_exclusion_multiple_with_space(self, sample_entur_api_response):
        responses.post(ENTUR_URL, json=sample_entur_api_response)

        parsed = json.loads(main(exclude_platforms=" A , 2 "))

        departures = parsed["departures"]
        # Platform A (FB1A) and platform 2 (line 2) should both be excluded
        assert "FB1A" not in departures
        assert 2 not in departures and "2" not in departures

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_no_exclusion_keeps_all(self, sample_entur_api_response):
        responses.post(ENTUR_URL, json=sample_entur_api_response)

        parsed = json.loads(main(exclude_platforms=""))

        assert parsed["num_departures"] == 4

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_minutes_to_fetch_as_string(self, sample_entur_api_response):
        """Documents the existing bug: string minutes_to_fetch gets converted correctly,
        but passing an int != 30 silently gets overwritten to 30."""
        responses.post(ENTUR_URL, json=sample_entur_api_response)

        # String "45" should work — the defensive code handles this case
        parsed = json.loads(main(minutes_to_fetch="45"))
        assert parsed["minutes_to_fetch"] == 45

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_minutes_to_fetch_as_int_bug(self, sample_entur_api_response):
        """Previously a bug: passing int 45 got silently overwritten to 30 by line 184.

        isinstance(45, str) is False, so the else branch fired: minutes_to_fetch = 30.
        Now fixed: int values are passed through unchanged.
        """
        responses.post(ENTUR_URL, json=sample_entur_api_response)

        parsed = json.loads(main(minutes_to_fetch=45))
        assert parsed["minutes_to_fetch"] == 45

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_departures_grouped_by_line(self, sample_entur_api_response):
        responses.post(ENTUR_URL, json=sample_entur_api_response)

        parsed = json.loads(main())
        departures = parsed["departures"]

        # Line 5 should have the Vestli destination
        assert "5" in departures
        vestli_key = [k for k in departures["5"] if "Vestli" in k]
        assert len(vestli_key) == 1
