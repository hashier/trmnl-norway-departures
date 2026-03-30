from collections import namedtuple
from trmnl import sort_key

Index = namedtuple("Index", ["line", "dst", "platform"])


class TestSortKey:
    def test_numeric_lines_sort_before_string_lines(self):
        """Local routes (numeric) should sort before regional (string like FB1A)."""
        numeric_item = (Index(line=5, dst="Vestli", platform="1"), [])
        string_item = (Index(line="FB1A", dst="Lillestrøm", platform="A"), [])

        assert sort_key(numeric_item) < sort_key(string_item)

    def test_numeric_lines_sort_by_number(self):
        line_2 = (Index(line=2, dst="Ellingsrudåsen", platform="2"), [])
        line_5 = (Index(line=5, dst="Vestli", platform="1"), [])

        assert sort_key(line_2) < sort_key(line_5)

    def test_same_line_sorts_by_platform(self):
        plat_1 = (Index(line=5, dst="Vestli", platform="1"), [])
        plat_2 = (Index(line=5, dst="Vestli", platform="2"), [])

        assert sort_key(plat_1) < sort_key(plat_2)

    def test_same_line_and_platform_sorts_by_destination(self):
        dst_a = (Index(line=5, dst="AAA", platform="1"), [])
        dst_b = (Index(line=5, dst="ZZZ", platform="1"), [])

        assert sort_key(dst_a) < sort_key(dst_b)

    def test_full_sort_order(self):
        """Verify end-to-end sorting of a mixed list."""
        items = [
            (Index(line="FB1A", dst="Lillestrøm", platform="A"), []),
            (Index(line=5, dst="Vestli", platform="1"), []),
            (Index(line=2, dst="Ellingsrudåsen", platform="2"), []),
            (Index(line=5, dst="Ringen", platform="1"), []),
        ]
        sorted_items = sorted(items, key=sort_key)
        lines = [item[0].line for item in sorted_items]
        assert lines == [2, 5, 5, "FB1A"]
