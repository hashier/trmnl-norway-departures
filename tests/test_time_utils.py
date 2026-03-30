from trmnl import iso_time_to_human


class TestIsoTimeToHuman:
    def test_basic_conversion(self):
        assert iso_time_to_human("2025-03-19T14:35:00+01:00") == "14:35.00"

    def test_preserves_seconds(self):
        assert iso_time_to_human("2025-03-19T14:35:42+01:00") == "14:35.42"

    def test_midnight(self):
        assert iso_time_to_human("2025-03-19T00:00:00+01:00") == "00:00.00"

    def test_different_timezone_offset(self):
        # The function formats in the time's own timezone, not UTC
        result = iso_time_to_human("2025-03-19T14:35:00+02:00")
        assert result == "14:35.00"

    def test_utc_time(self):
        result = iso_time_to_human("2025-03-19T14:35:00+00:00")
        assert result == "14:35.00"
