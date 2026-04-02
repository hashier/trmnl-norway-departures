import pytest
from trmnl import create_stripped_item, group_data_by_line_dst_platform


class TestCreateStrippedItem:
    def test_extracts_correct_fields(self, sample_departure_item):
        result = create_stripped_item(sample_departure_item)

        assert result == {
            "schedule": "14:35.00",
            "expected": "14:36.00",
            "type": "metro",
        }

    def test_on_time_departure(self):
        """When aimed and expected are the same."""
        item = {
            "aimedDepartureTime": "2025-03-19T14:40:00+01:00",
            "expectedDepartureTime": "2025-03-19T14:40:00+01:00",
            "serviceJourney": {
                "line": {"publicCode": "2", "transportMode": "metro"}
            },
        }
        result = create_stripped_item(item)
        assert result["schedule"] == result["expected"]

    def test_missing_aimed_departure_time_raises(self):
        """Missing required field should raise KeyError."""
        item = {
            "expectedDepartureTime": "2025-03-19T14:36:00+01:00",
            "serviceJourney": {"line": {"publicCode": "5", "transportMode": "metro"}},
        }
        with pytest.raises(KeyError):
            create_stripped_item(item)

    def test_missing_service_journey_raises(self):
        item = {
            "aimedDepartureTime": "2025-03-19T14:35:00+01:00",
            "expectedDepartureTime": "2025-03-19T14:36:00+01:00",
        }
        with pytest.raises(KeyError):
            create_stripped_item(item)

    def test_different_transport_modes(self):
        for mode in ["bus", "tram", "rail", "water", "coach"]:
            item = {
                "aimedDepartureTime": "2025-03-19T14:35:00+01:00",
                "expectedDepartureTime": "2025-03-19T14:36:00+01:00",
                "serviceJourney": {"line": {"publicCode": "1", "transportMode": mode}},
            }
            result = create_stripped_item(item)
            assert result["type"] == mode

    def test_only_returns_three_fields(self):
        """Stripped item should contain exactly schedule, expected, and type."""
        item = {
            "destinationDisplay": {"frontText": "Vestli"},
            "situations": [{"summary": {"value": "Delayed"}}],
            "quay": {"publicCode": "1"},
            "aimedDepartureTime": "2025-03-19T14:35:00+01:00",
            "expectedDepartureTime": "2025-03-19T14:36:00+01:00",
            "actualDepartureTime": "2025-03-19T14:37:00+01:00",
            "serviceJourney": {"line": {"publicCode": "5", "transportMode": "metro"}},
        }
        result = create_stripped_item(item)
        assert set(result.keys()) == {"schedule", "expected", "type"}


class TestGroupDataByLineDstPlatform:
    def test_groups_same_line_and_destination(self, sample_departure_items):
        grouped = group_data_by_line_dst_platform(sample_departure_items)

        # Two line-5-Vestli departures should be grouped together
        matching = [
            v for k, v in grouped.items() if k.line == 5 and k.dst == "Vestli"
        ]
        assert len(matching) == 1
        assert len(matching[0]) == 2  # two departures

    def test_numeric_line_converted_to_int(self, sample_departure_items):
        grouped = group_data_by_line_dst_platform(sample_departure_items)

        line_types = {type(k.line) for k in grouped.keys()}
        # "5" and "2" become int, "FB1A" stays str
        assert int in line_types
        assert str in line_types

    def test_string_line_stays_string(self, sample_departure_items):
        grouped = group_data_by_line_dst_platform(sample_departure_items)

        string_lines = [k for k in grouped.keys() if isinstance(k.line, str)]
        assert len(string_lines) == 1
        assert string_lines[0].line == "FB1A"

    def test_different_platforms_create_separate_groups(self):
        """Same line, same destination, different platforms = separate groups."""
        items = [
            {
                "destinationDisplay": {"frontText": "Vestli"},
                "quay": {"publicCode": "1"},
                "expectedDepartureTime": "2025-03-19T14:36:00+01:00",
                "aimedDepartureTime": "2025-03-19T14:35:00+01:00",
                "serviceJourney": {
                    "line": {"publicCode": "5", "transportMode": "metro"}
                },
            },
            {
                "destinationDisplay": {"frontText": "Vestli"},
                "quay": {"publicCode": "3"},
                "expectedDepartureTime": "2025-03-19T14:46:00+01:00",
                "aimedDepartureTime": "2025-03-19T14:45:00+01:00",
                "serviceJourney": {
                    "line": {"publicCode": "5", "transportMode": "metro"}
                },
            },
        ]
        grouped = group_data_by_line_dst_platform(items)
        assert len(grouped) == 2

    def test_empty_data(self):
        grouped = group_data_by_line_dst_platform([])
        assert grouped == {}

    def test_none_platform(self):
        """Stops that have no platform info (quay publicCode is None)."""
        items = [
            {
                "destinationDisplay": {"frontText": "Somewhere"},
                "quay": {"publicCode": None},
                "expectedDepartureTime": "2025-03-19T14:36:00+01:00",
                "aimedDepartureTime": "2025-03-19T14:35:00+01:00",
                "serviceJourney": {
                    "line": {"publicCode": "100", "transportMode": "bus"}
                },
            },
        ]
        grouped = group_data_by_line_dst_platform(items)
        keys = list(grouped.keys())
        assert len(keys) == 1
        assert keys[0].platform is None
