import unittest
from datetime import timezone, timedelta

from utc_offset_parser import parse_utc_offset, ParseError


class ParseUtcOffsetTests(unittest.TestCase):
    def test_colon_form_with_utc_prefix(self):
        tz = parse_utc_offset("UTC+02:00")
        self.assertEqual(tz.utcoffset(None), timedelta(hours=2))
        self.assertEqual(tz.tzname(None), "UTC+02:00")

    def test_colon_form_with_gmt_prefix(self):
        tz = parse_utc_offset("GMT-05:30")
        self.assertEqual(tz.utcoffset(None), timedelta(hours=-5, minutes=-30))

    def test_colon_form_no_prefix(self):
        tz = parse_utc_offset("+02:00")
        self.assertEqual(tz.utcoffset(None), timedelta(hours=2))

    def test_compact_hhmm(self):
        tz = parse_utc_offset("+0530")
        self.assertEqual(tz.utcoffset(None), timedelta(hours=5, minutes=30))

    def test_compact_hhmm_negative(self):
        tz = parse_utc_offset("-0530")
        self.assertEqual(tz.utcoffset(None), timedelta(hours=-5, minutes=-30))

    def test_hours_only(self):
        tz = parse_utc_offset("+05")
        self.assertEqual(tz.utcoffset(None), timedelta(hours=5))

    def test_hours_only_negative(self):
        tz = parse_utc_offset("-05")
        self.assertEqual(tz.utcoffset(None), timedelta(hours=-5))

    def test_zero_offset(self):
        tz = parse_utc_offset("+00:00")
        self.assertEqual(tz.utcoffset(None), timedelta(0))

    def test_lowercase_prefix(self):
        tz = parse_utc_offset("utc+02:00")
        self.assertEqual(tz.utcoffset(None), timedelta(hours=2))

    def test_whitespace_stripped(self):
        tz = parse_utc_offset("  +02:00  ")
        self.assertEqual(tz.utcoffset(None), timedelta(hours=2))

    def test_rejects_missing_sign(self):
        with self.assertRaises(ParseError):
            parse_utc_offset("02:00")

    def test_rejects_bare_utc(self):
        with self.assertRaises(ParseError):
            parse_utc_offset("UTC")

    def test_rejects_bare_z(self):
        with self.assertRaises(ParseError):
            parse_utc_offset("Z")

    def test_rejects_hour_out_of_range(self):
        with self.assertRaises(ParseError):
            parse_utc_offset("+24:00")

    def test_rejects_minute_out_of_range(self):
        with self.assertRaises(ParseError):
            parse_utc_offset("+02:60")

    def test_rejects_non_string(self):
        with self.assertRaises(ParseError):
            parse_utc_offset(530)  # type: ignore[arg-type]

    def test_rejects_single_digit_hour(self):
        with self.assertRaises(ParseError):
            parse_utc_offset("+2:00")


if __name__ == "__main__":
    unittest.main()
