import pytest
from collections import namedtuple


@pytest.fixture
def sample_departure_item():
    """A single departure item as returned by the Entur API."""
    return {
        "destinationDisplay": {"frontText": "Vestli"},
        "situations": [],
        "quay": {"publicCode": "1"},
        "expectedDepartureTime": "2025-03-19T14:36:00+01:00",
        "actualDepartureTime": None,
        "aimedDepartureTime": "2025-03-19T14:35:00+01:00",
        "serviceJourney": {
            "line": {
                "publicCode": "5",
                "transportMode": "metro",
            }
        },
    }


@pytest.fixture
def sample_departure_items():
    """Multiple departure items spanning different lines, destinations, and platforms."""
    return [
        {
            "destinationDisplay": {"frontText": "Vestli"},
            "situations": [],
            "quay": {"publicCode": "1"},
            "expectedDepartureTime": "2025-03-19T14:36:00+01:00",
            "actualDepartureTime": None,
            "aimedDepartureTime": "2025-03-19T14:35:00+01:00",
            "serviceJourney": {
                "line": {"publicCode": "5", "transportMode": "metro"}
            },
        },
        {
            "destinationDisplay": {"frontText": "Vestli"},
            "situations": [],
            "quay": {"publicCode": "1"},
            "expectedDepartureTime": "2025-03-19T14:46:00+01:00",
            "actualDepartureTime": None,
            "aimedDepartureTime": "2025-03-19T14:45:00+01:00",
            "serviceJourney": {
                "line": {"publicCode": "5", "transportMode": "metro"}
            },
        },
        {
            "destinationDisplay": {"frontText": "Ellingsrudåsen"},
            "situations": [],
            "quay": {"publicCode": "2"},
            "expectedDepartureTime": "2025-03-19T14:40:00+01:00",
            "actualDepartureTime": None,
            "aimedDepartureTime": "2025-03-19T14:40:00+01:00",
            "serviceJourney": {
                "line": {"publicCode": "2", "transportMode": "metro"}
            },
        },
        {
            "destinationDisplay": {"frontText": "Lillestrøm"},
            "situations": [],
            "quay": {"publicCode": "A"},
            "expectedDepartureTime": "2025-03-19T14:50:00+01:00",
            "actualDepartureTime": None,
            "aimedDepartureTime": "2025-03-19T14:48:00+01:00",
            "serviceJourney": {
                "line": {"publicCode": "FB1A", "transportMode": "rail"}
            },
        },
    ]


@pytest.fixture
def sample_entur_api_response(sample_departure_items):
    """A full Entur API JSON response wrapping departure items."""
    return {
        "data": {
            "board1": [
                {
                    "name": "Jernbanetorget",
                    "estimatedCalls": sample_departure_items,
                }
            ]
        }
    }


@pytest.fixture
def Index():
    """The namedtuple used as dict keys in grouped data."""
    return namedtuple("Index", ["line", "dst", "platform"])
