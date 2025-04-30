from django.test import TestCase

from ..utils import simplify_location, generate_recurring_listing_slots
from datetime import datetime, timedelta, time


class SimplifyLocationTests(TestCase):
    def test_empty_string(self):
        """An empty location string should return an empty string."""
        self.assertEqual(simplify_location(""), "")

    def test_single_part(self):
        """A location string without a comma should be returned as-is."""
        self.assertEqual(simplify_location("Central Park"), "Central Park")

    def test_exact_two_parts_with_known_city(self):
        """
        For a location string with exactly two parts where the second part
        is a known city, the function returns "building, street, city".
        In this case, both street and city are the same.
        """
        input_str = "Empire State Building, Manhattan"
        # building = "Empire State Building", street = "Manhattan", and since "Manhattan" is in the list,
        # city will be "Manhattan". Expected result is "Empire State Building, Manhattan, Manhattan".
        expected = "Empire State Building, Manhattan, Manhattan"
        self.assertEqual(simplify_location(input_str), expected)

    def test_non_institution_no_known_city(self):
        """
        For a non-educational address without any part matching a known city,
        the default city "New York" is used.
        """
        input_str = "123 Main St, Suite 100, Some Suburb"
        # building = "123 Main St", street = "Suite 100", city defaults to "New York"
        expected = "123 Main St, Suite 100, New York"
        self.assertEqual(simplify_location(input_str), expected)

    def test_with_coordinates(self):
        """
        Coordinates (inside square brackets) are stripped out before processing.
        """
        input_str = "123 Main St, Suite 100, Some Suburb [40.123, -73.456]"
        expected = "123 Main St, Suite 100, New York"
        self.assertEqual(simplify_location(input_str), expected)

    def test_educational_institution(self):
        """
        For educational institutions, only the building and the city are returned.
        """
        input_str = "Tandon School of Engineering, Johnson Street, Downtown Brooklyn, Manhattan, New York"
        # parts: ["Tandon School of Engineering", "Johnson Street", "Downtown Brooklyn", "Manhattan", "New York"]
        # The generator will find "Manhattan" in parts (the first match in the known list).
        expected = "Tandon School of Engineering, Manhattan"
        self.assertEqual(simplify_location(input_str), expected)

    def test_extra_spaces(self):
        """
        Extra spaces should be stripped.
        """
        input_str = "  456 Elm St  ,   Queens  , Extra Info "
        # parts become: ["456 Elm St", "Queens", "Extra Info"]
        # building = "456 Elm St", street = "Queens", and since "Queens" is a known city,
        # expected = "456 Elm St, Queens, Queens"
        expected = "456 Elm St, Queens, Queens"
        self.assertEqual(simplify_location(input_str), expected)


class RecurringListingSlotsTests(TestCase):
    """Tests for the generate_recurring_listing_slots utility function"""

    def test_daily_pattern(self):
        """Test generating daily recurring slots"""
        # Use dynamic dates based on today
        today = datetime.today().date()
        start_date = today + timedelta(days=1)  # Tomorrow
        end_date = today + timedelta(days=3)  # 3 days from today
        start_time = time(9, 0)
        end_time = time(17, 0)

        slots = generate_recurring_listing_slots(
            start_date=start_date,
            start_time=start_time,
            end_time=end_time,
            pattern="daily",
            end_date=end_date,
        )

        # Should generate 3 slots (for 3 days)
        self.assertEqual(len(slots), 3)

        # Check first slot is tomorrow
        self.assertEqual(slots[0]["start_date"], start_date)
        self.assertEqual(slots[0]["start_time"], start_time)
        self.assertEqual(
            slots[0]["end_date"], start_date
        )  # Same day since not overnight
        self.assertEqual(slots[0]["end_time"], end_time)

        # Check last slot is end_date
        self.assertEqual(slots[2]["start_date"], end_date)
        self.assertEqual(slots[2]["end_time"], end_time)

    def test_daily_pattern_single_day(self):
        """Test daily pattern with start_date = end_date (edge case)"""
        today = datetime.today().date()
        start_date = today + timedelta(days=1)  # Tomorrow
        start_time = time(9, 0)
        end_time = time(17, 0)

        slots = generate_recurring_listing_slots(
            start_date=start_date,
            start_time=start_time,
            end_time=end_time,
            pattern="daily",
            end_date=start_date,  # Same day
        )

        # Should generate exactly 1 slot
        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0]["start_date"], start_date)
        self.assertEqual(slots[0]["end_date"], start_date)

    def test_weekly_pattern(self):
        """Test generating weekly recurring slots"""
        today = datetime.today().date()
        start_date = today + timedelta(days=1)  # Tomorrow
        start_time = time(9, 0)
        end_time = time(17, 0)
        weeks = 3

        slots = generate_recurring_listing_slots(
            start_date=start_date,
            start_time=start_time,
            end_time=end_time,
            pattern="weekly",
            weeks=weeks,
        )

        # Should generate 3 slots (for 3 weeks)
        self.assertEqual(len(slots), 3)

        # Check dates are one week apart
        self.assertEqual(slots[0]["start_date"], start_date)
        self.assertEqual(slots[1]["start_date"], start_date + timedelta(weeks=1))
        self.assertEqual(slots[2]["start_date"], start_date + timedelta(weeks=2))

        # Check times are consistent
        for slot in slots:
            self.assertEqual(slot["start_time"], start_time)
            self.assertEqual(slot["end_time"], end_time)

    def test_overnight_daily_pattern(self):
        """Test overnight slots with daily pattern"""
        today = datetime.today().date()
        start_date = today + timedelta(days=1)  # Tomorrow
        end_date = today + timedelta(days=2)  # Day after tomorrow
        start_time = time(20, 0)  # 8 PM
        end_time = time(8, 0)  # 8 AM

        slots = generate_recurring_listing_slots(
            start_date=start_date,
            start_time=start_time,
            end_time=end_time,
            pattern="daily",
            is_overnight=True,
            end_date=end_date,
        )

        # Should generate 2 slots
        self.assertEqual(len(slots), 2)

        # Check overnight dates (end_date should be day after start_date)
        for slot in slots:
            self.assertEqual(slot["end_date"], slot["start_date"] + timedelta(days=1))

    def test_overnight_weekly_pattern(self):
        """Test overnight slots with weekly pattern"""
        today = datetime.today().date()
        start_date = today + timedelta(days=1)  # Tomorrow
        start_time = time(20, 0)  # 8 PM
        end_time = time(8, 0)  # 8 AM

        slots = generate_recurring_listing_slots(
            start_date=start_date,
            start_time=start_time,
            end_time=end_time,
            pattern="weekly",
            is_overnight=True,
            weeks=2,
        )

        # Should generate 2 slots (for 2 weeks)
        self.assertEqual(len(slots), 2)

        # Check overnight dates and weekly separation
        self.assertEqual(slots[0]["start_date"], start_date)
        self.assertEqual(slots[0]["end_date"], start_date + timedelta(days=1))
        self.assertEqual(slots[1]["start_date"], start_date + timedelta(weeks=1))
        self.assertEqual(slots[1]["end_date"], start_date + timedelta(weeks=1, days=1))

    def test_missing_end_date_for_daily(self):
        """Test error when end_date is missing for daily pattern"""
        today = datetime.today().date()
        start_date = today + timedelta(days=1)  # Tomorrow
        start_time = time(9, 0)
        end_time = time(17, 0)

        with self.assertRaises(ValueError) as context:
            generate_recurring_listing_slots(
                start_date=start_date,
                start_time=start_time,
                end_time=end_time,
                pattern="daily",
                # Missing end_date
            )

        self.assertIn("End date is required", str(context.exception))

    def test_missing_weeks_for_weekly(self):
        """Test error when weeks is missing for weekly pattern"""
        today = datetime.today().date()
        start_date = today + timedelta(days=1)  # Tomorrow
        start_time = time(9, 0)
        end_time = time(17, 0)

        with self.assertRaises(ValueError) as context:
            generate_recurring_listing_slots(
                start_date=start_date,
                start_time=start_time,
                end_time=end_time,
                pattern="weekly",
                # Missing weeks
            )

        self.assertIn("Number of weeks is required", str(context.exception))

    def test_invalid_pattern(self):
        """Test error for invalid pattern"""
        today = datetime.today().date()
        start_date = today + timedelta(days=1)  # Tomorrow
        start_time = time(9, 0)
        end_time = time(17, 0)

        with self.assertRaises(ValueError) as context:
            generate_recurring_listing_slots(
                start_date=start_date,
                start_time=start_time,
                end_time=end_time,
                pattern="monthly",  # Invalid pattern
            )

        self.assertIn("Unknown pattern", str(context.exception))
