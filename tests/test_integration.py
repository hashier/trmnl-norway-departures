"""Integration tests that run main() with the same parameters from the bottom of trmnl.py
and verify the full transformation pipeline against stored snapshots.

These test cases come from the commented-out invocations in trmnl.py lines 258-263.
"""
import json

import responses
from freezegun import freeze_time

from trmnl import main

ENTUR_URL = "https://api.entur.io/journey-planner/v3/graphql"

# A rich fixture covering diverse scenarios:
# - Numeric line codes (metro 2, 3, 5; tram 17; bus 100)
# - String line codes (rail FB1A, RE11)
# - Platforms 1, 2, 3, A, B, and None
# - On-time and delayed departures
RICH_DEPARTURES = [
    {
        "destinationDisplay": {"frontText": "Vestli"},
        "situations": [],
        "quay": {"publicCode": "1"},
        "expectedDepartureTime": "2025-03-19T14:36:00+01:00",
        "actualDepartureTime": None,
        "aimedDepartureTime": "2025-03-19T14:36:00+01:00",
        "serviceJourney": {"line": {"publicCode": "5", "transportMode": "metro"}},
    },
    {
        "destinationDisplay": {"frontText": "Vestli"},
        "situations": [],
        "quay": {"publicCode": "1"},
        "expectedDepartureTime": "2025-03-19T14:47:00+01:00",
        "actualDepartureTime": None,
        "aimedDepartureTime": "2025-03-19T14:45:00+01:00",
        "serviceJourney": {"line": {"publicCode": "5", "transportMode": "metro"}},
    },
    {
        "destinationDisplay": {"frontText": "Ellingsrudåsen"},
        "situations": [],
        "quay": {"publicCode": "2"},
        "expectedDepartureTime": "2025-03-19T14:40:00+01:00",
        "actualDepartureTime": None,
        "aimedDepartureTime": "2025-03-19T14:40:00+01:00",
        "serviceJourney": {"line": {"publicCode": "2", "transportMode": "metro"}},
    },
    {
        "destinationDisplay": {"frontText": "Mortensrud"},
        "situations": [],
        "quay": {"publicCode": "3"},
        "expectedDepartureTime": "2025-03-19T14:42:00+01:00",
        "actualDepartureTime": None,
        "aimedDepartureTime": "2025-03-19T14:42:00+01:00",
        "serviceJourney": {"line": {"publicCode": "3", "transportMode": "metro"}},
    },
    {
        "destinationDisplay": {"frontText": "Rikshospitalet"},
        "situations": [],
        "quay": {"publicCode": "1"},
        "expectedDepartureTime": "2025-03-19T14:50:00+01:00",
        "actualDepartureTime": None,
        "aimedDepartureTime": "2025-03-19T14:48:00+01:00",
        "serviceJourney": {"line": {"publicCode": "17", "transportMode": "tram"}},
    },
    {
        "destinationDisplay": {"frontText": "Lillestrøm"},
        "situations": [],
        "quay": {"publicCode": "A"},
        "expectedDepartureTime": "2025-03-19T14:55:00+01:00",
        "actualDepartureTime": None,
        "aimedDepartureTime": "2025-03-19T14:52:00+01:00",
        "serviceJourney": {"line": {"publicCode": "FB1A", "transportMode": "rail"}},
    },
    {
        "destinationDisplay": {"frontText": "Drammen"},
        "situations": [],
        "quay": {"publicCode": "B"},
        "expectedDepartureTime": "2025-03-19T15:05:00+01:00",
        "actualDepartureTime": None,
        "aimedDepartureTime": "2025-03-19T15:00:00+01:00",
        "serviceJourney": {"line": {"publicCode": "RE11", "transportMode": "rail"}},
    },
    {
        "destinationDisplay": {"frontText": "Somewhere"},
        "situations": [],
        "quay": {"publicCode": None},
        "expectedDepartureTime": "2025-03-19T15:10:00+01:00",
        "actualDepartureTime": None,
        "aimedDepartureTime": "2025-03-19T15:10:00+01:00",
        "serviceJourney": {"line": {"publicCode": "100", "transportMode": "bus"}},
    },
]

ENTUR_API_RESPONSE = {
    "data": {
        "board1": [{"name": "Teststasjonen", "estimatedCalls": RICH_DEPARTURES}]
    }
}


class TestIntegrationExcludePlatformsAB:
    """trmnl.py line 258:
    main(entur_stop="NSR:StopPlace:11356", exclude_platforms="A,B",
         minutes_to_fetch=90, ignore_departures_within_the_next_minutes=5)
    Scenario: 'No platform info available' — exercises platform exclusion + None platform.
    """

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_full_output(self):
        responses.post(ENTUR_URL, json=ENTUR_API_RESPONSE)

        result = json.loads(
            main(
                entur_stop="NSR:StopPlace:11356",
                exclude_platforms="A,B",
                minutes_to_fetch=90,
                ignore_departures_within_the_next_minutes=5,
            )
        )

        # -- Metadata --
        assert result["name"] == "Teststasjonen"
        assert result["last_updated"] == "12:00"
        assert result["num_departures"] == 8
        assert result["num_departures-excludes"] == 6  # 8 - FB1A(A) - RE11(B)
        assert result["exclude_platforms"] == "A,B"
        assert result["fetch_limit"] == 200
        # Fixed: minutes_to_fetch=90 (int) is now passed through correctly
        assert result["minutes_to_fetch"] == 90

        # -- Departures structure --
        deps = result["departures"]

        # Platforms A and B are excluded
        assert "FB1A" not in deps
        assert "RE11" not in deps

        # Numeric lines present and sorted by line number
        assert list(deps.keys()) == ["2", "3", "5", "17", "100"]

        # Line 5 has two departures (second is delayed)
        assert deps["5"] == {
            "Vestli - 1": [
                {"schedule": "14:36.00", "expected": "14:36.00", "type": "metro"},
                {"schedule": "14:45.00", "expected": "14:47.00", "type": "metro"},
            ]
        }

        # Line 2: on-time metro
        assert deps["2"] == {
            "Ellingsrudåsen - 2": [
                {"schedule": "14:40.00", "expected": "14:40.00", "type": "metro"}
            ]
        }

        # Line 17: delayed tram
        assert deps["17"] == {
            "Rikshospitalet - 1": [
                {"schedule": "14:48.00", "expected": "14:50.00", "type": "tram"}
            ]
        }

        # Line 100: None platform — key has no " - None" suffix
        assert deps["100"] == {
            "Somewhere": [
                {"schedule": "15:10.00", "expected": "15:10.00", "type": "bus"}
            ]
        }


class TestIntegrationIntMinutes:
    """trmnl.py line 259:
    main(entur_stop="NSR:StopPlace:58366", exclude_platforms="",
         minutes_to_fetch=7, ignore_departures_within_the_next_minutes=15)
    Scenario: int check for minutes_to_fetch — no exclusions, all departures present.
    """

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_full_output(self):
        responses.post(ENTUR_URL, json=ENTUR_API_RESPONSE)

        result = json.loads(
            main(
                entur_stop="NSR:StopPlace:58366",
                exclude_platforms="",
                minutes_to_fetch=7,
                ignore_departures_within_the_next_minutes=15,
            )
        )

        # -- Metadata --
        assert result["name"] == "Teststasjonen"
        assert result["num_departures"] == 8
        assert result["num_departures-excludes"] == 8  # no exclusions
        assert result["exclude_platforms"] == ""
        # Fixed: minutes_to_fetch=7 (int) is now passed through correctly
        assert result["minutes_to_fetch"] == 7

        # -- All lines present including rail --
        deps = result["departures"]
        assert list(deps.keys()) == ["2", "3", "5", "17", "100", "FB1A", "RE11"]

        # Rail lines with platform info
        assert deps["FB1A"] == {
            "Lillestrøm - A": [
                {"schedule": "14:52.00", "expected": "14:55.00", "type": "rail"}
            ]
        }
        assert deps["RE11"] == {
            "Drammen - B": [
                {"schedule": "15:00.00", "expected": "15:05.00", "type": "rail"}
            ]
        }


class TestIntegrationStrMinutes:
    """trmnl.py line 260:
    main(entur_stop="NSR:StopPlace:58366", exclude_platforms="",
         minutes_to_fetch="29", ignore_departures_within_the_next_minutes=15)
    Scenario: str check for minutes_to_fetch — string "29" should be parsed to int 29.
    """

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_full_output(self):
        responses.post(ENTUR_URL, json=ENTUR_API_RESPONSE)

        result = json.loads(
            main(
                entur_stop="NSR:StopPlace:58366",
                exclude_platforms="",
                minutes_to_fetch="29",
                ignore_departures_within_the_next_minutes=15,
            )
        )

        # String minutes correctly parsed — this path works
        assert result["minutes_to_fetch"] == 29
        assert result["num_departures"] == 8
        assert result["num_departures-excludes"] == 8

        # Same departure structure as int_minutes case (no exclusions)
        deps = result["departures"]
        assert list(deps.keys()) == ["2", "3", "5", "17", "100", "FB1A", "RE11"]


class TestIntegrationHomeDefault:
    """trmnl.py line 263:
    main(entur_stop="NSR:StopPlace:58189", exclude_platforms="A,B",
         minutes_to_fetch=30, ignore_departures_within_the_next_minutes=15)
    Scenario: Default home stop — excludes platforms A and B.
    """

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_full_output(self):
        responses.post(ENTUR_URL, json=ENTUR_API_RESPONSE)

        result = json.loads(
            main(
                entur_stop="NSR:StopPlace:58189",
                exclude_platforms="A,B",
                minutes_to_fetch=30,
                ignore_departures_within_the_next_minutes=15,
            )
        )

        # -- Metadata --
        assert result["name"] == "Teststasjonen"
        assert result["last_updated"] == "12:00"
        assert result["minutes_to_fetch"] == 30
        assert result["num_departures"] == 8
        assert result["num_departures-excludes"] == 6
        assert result["exclude_platforms"] == "A,B"

        # -- Full snapshot of departures --
        assert result["departures"] == {
            "2": {
                "Ellingsrudåsen - 2": [
                    {"schedule": "14:40.00", "expected": "14:40.00", "type": "metro"}
                ]
            },
            "3": {
                "Mortensrud - 3": [
                    {"schedule": "14:42.00", "expected": "14:42.00", "type": "metro"}
                ]
            },
            "5": {
                "Vestli - 1": [
                    {"schedule": "14:36.00", "expected": "14:36.00", "type": "metro"},
                    {"schedule": "14:45.00", "expected": "14:47.00", "type": "metro"},
                ]
            },
            "17": {
                "Rikshospitalet - 1": [
                    {"schedule": "14:48.00", "expected": "14:50.00", "type": "tram"}
                ]
            },
            "100": {
                "Somewhere": [
                    {"schedule": "15:10.00", "expected": "15:10.00", "type": "bus"}
                ]
            },
        }

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_delayed_departure_shows_both_times(self):
        """Line 5 second departure: aimed 14:45, expected 14:47 (2 min delay)."""
        responses.post(ENTUR_URL, json=ENTUR_API_RESPONSE)

        result = json.loads(
            main(entur_stop="NSR:StopPlace:58189", exclude_platforms="A,B")
        )
        vestli_deps = result["departures"]["5"]["Vestli - 1"]
        delayed = vestli_deps[1]

        assert delayed["schedule"] == "14:45.00"
        assert delayed["expected"] == "14:47.00"
        assert delayed["schedule"] != delayed["expected"]

    @responses.activate
    @freeze_time("2025-03-19T12:00:00", tz_offset=0)
    def test_none_platform_omits_suffix(self):
        """Bus 100 has no platform — the key should be just the destination, no ' - None'."""
        responses.post(ENTUR_URL, json=ENTUR_API_RESPONSE)

        result = json.loads(
            main(entur_stop="NSR:StopPlace:58189", exclude_platforms="A,B")
        )
        bus_100 = result["departures"]["100"]

        assert "Somewhere" in bus_100
        assert "Somewhere - None" not in bus_100

class TestIntegrationEmptyStringPlatform:
    """Bug report: some Entur departures have publicCode: "" instead of null.
    Bug id on github: https://github.com/hashier/trmnl-norway-departures/pull/2

    Test data based on the Rosenhoff stop example from the bug report:
    - Bus 380 to Lillestrøm with publicCode: null (handled correctly)
    - Tram 17 to Sinsen-Grefsen st. with publicCode: "" (the problematic case)
    """

    ROSENHOFF_DEPARTURES = [
        {
            "destinationDisplay": {"frontText": "Lillestrøm"},
            "situations": [],
            "quay": {"publicCode": None},
            "expectedDepartureTime": "2026-03-07T16:52:00+01:00",
            "actualDepartureTime": None,
            "aimedDepartureTime": "2026-03-07T16:52:00+01:00",
            "serviceJourney": {"line": {"publicCode": "380", "transportMode": "bus"}},
        },
        {
            "destinationDisplay": {"frontText": "Sinsen-Grefsen st."},
            "situations": [],
            "quay": {"publicCode": ""},
            "expectedDepartureTime": "2026-03-07T16:33:27+01:00",
            "actualDepartureTime": None,
            "aimedDepartureTime": "2026-03-07T16:33:00+01:00",
            "serviceJourney": {"line": {"publicCode": "17", "transportMode": "tram"}},
        },
    ]

    ROSENHOFF_API_RESPONSE = {
        "data": {
            "board1": [
                {"name": "Rosenhoff", "estimatedCalls": ROSENHOFF_DEPARTURES}
            ]
        }
    }

    @responses.activate
    @freeze_time("2026-03-07T15:00:00", tz_offset=0)
    def test_empty_string_platform_not_excluded_by_empty_exclude_list(self):
        """With exclude_platforms="", a departure with publicCode="" must NOT be dropped."""
        responses.post(ENTUR_URL, json=self.ROSENHOFF_API_RESPONSE)

        result = json.loads(main(exclude_platforms=""))
        deps = result["departures"]

        # Both lines must be present
        assert "17" in deps, "Tram 17 with empty-string platform was incorrectly excluded"
        assert "380" in deps

    @responses.activate
    @freeze_time("2026-03-07T15:00:00", tz_offset=0)
    def test_empty_string_platform_not_excluded_by_named_exclude(self):
        """With exclude_platforms="X", a departure with publicCode="" must NOT be dropped."""
        responses.post(ENTUR_URL, json=self.ROSENHOFF_API_RESPONSE)

        result = json.loads(main(exclude_platforms="X"))
        deps = result["departures"]

        assert "17" in deps
        assert "380" in deps

    @responses.activate
    @freeze_time("2026-03-07T15:00:00", tz_offset=0)
    def test_both_departures_counted(self):
        """Both departures should be counted in the totals."""
        responses.post(ENTUR_URL, json=self.ROSENHOFF_API_RESPONSE)

        result = json.loads(main(exclude_platforms=""))

        assert result["num_departures"] == 2
        assert result["num_departures-excludes"] == 2

    @responses.activate
    @freeze_time("2026-03-07T15:00:00", tz_offset=0)
    def test_empty_string_platform_display_key(self):
        """BUG: publicCode "" produces a dangling ' - ' suffix in the destination key.

        The check `item[0].platform != None` is True for "", so it renders
        "Sinsen-Grefsen st. - " instead of just "Sinsen-Grefsen st.".
        This test documents the current (buggy) behavior.
        """
        responses.post(ENTUR_URL, json=self.ROSENHOFF_API_RESPONSE)

        result = json.loads(main(exclude_platforms=""))
        tram_17 = result["departures"]["17"]

        # Current behavior: dangling " - " suffix (bug)
        assert "Sinsen-Grefsen st. - " in tram_17
        # After fix, it should be just the destination:
        # assert "Sinsen-Grefsen st." in tram_17

    @responses.activate
    @freeze_time("2026-03-07T15:00:00", tz_offset=0)
    def test_null_platform_display_key_no_suffix(self):
        """Null platform correctly omits the suffix — contrast with empty string."""
        responses.post(ENTUR_URL, json=self.ROSENHOFF_API_RESPONSE)

        result = json.loads(main(exclude_platforms=""))
        bus_380 = result["departures"]["380"]

        assert "Lillestrøm" in bus_380
        assert "Lillestrøm - " not in bus_380
