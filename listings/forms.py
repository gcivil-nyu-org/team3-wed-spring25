import datetime
import pytz
from django import forms
from django.utils import timezone
from .models import Listing, Review
from .models import Review

# Generate half-hour choices for 00:00 -> 23:30
HALF_HOUR_CHOICES = [
    (f"{hour:02d}:{minute:02d}", f"{hour:02d}:{minute:02d}")
    for hour in range(24)
    for minute in (0, 30)
]


class ListingForm(forms.ModelForm):
    # Use ChoiceFields for half-hour increments
    available_time_from = forms.ChoiceField(
        choices=HALF_HOUR_CHOICES,
        label="Available Time From",
    )
    available_time_until = forms.ChoiceField(
        choices=HALF_HOUR_CHOICES,
        label="Available Time Until",
    )

    class Meta:
        model = Listing
        fields = [
            "title",
            "location",
            "rent_per_hour",
            "description",
            "available_from",
            "available_until",
            "available_time_from",
            "available_time_until",
        ]
        widgets = {
            "available_from": forms.DateInput(attrs={"type": "date"}),
            "available_until": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_available_from(self):
        """
        Validates that the 'available_from' date is not in the past.
        Ensures the comparison is done in the correct timezone (New York).
        """
        available_from = self.cleaned_data.get("available_from")
        nyc_tz = pytz.timezone("America/New_York")
        today = timezone.now().astimezone(nyc_tz).date()

        if available_from:
            # Ensure the value is a date object
            if isinstance(available_from, datetime.datetime):
                available_from = available_from.date()

            # Validation: 'available_from' should not be in the past
            if available_from < today:
                raise forms.ValidationError(
                    "The 'Available From' date cannot be in the past."
                )

        return available_from

    def clean_available_until(self):
        """
        Validates that the 'available_until' date is not in the past and is after 'available_from'.
        """
        available_from = self.cleaned_data.get("available_from")
        available_until = self.cleaned_data.get("available_until")
        nyc_tz = pytz.timezone("America/New_York")
        today = timezone.now().astimezone(nyc_tz).date()

        if available_until:
            if available_until < today:
                raise forms.ValidationError(
                    "The 'Available Until' date cannot be in the past."
                )
            if available_from and available_until < available_from:
                raise forms.ValidationError(
                    "The 'Available Until' date cannot be before the 'Available From' date."
                )

        return available_until

    def clean(self):
        """
        Validates that:
        - Available From date is before Available Until.
        - Rent per hour is positive.
        - Available Time From is before Available Time Until.
        - Allows overnight bookings if dates are different.
        """
        cleaned_data = super().clean()
        errors = []

        available_from = cleaned_data.get("available_from")
        available_until = cleaned_data.get("available_until")
        time_from_str = cleaned_data.get("available_time_from")  # e.g., '08:00'
        time_until_str = cleaned_data.get("available_time_until")  # e.g., '12:30'
        rent_per_hour = cleaned_data.get("rent_per_hour")

        # Validate dates
        if available_from and available_until and available_from >= available_until:
            errors.append("Available From date must be before Available Until date.")

        # Validate rent amount
        if rent_per_hour is not None and rent_per_hour <= 0:
            errors.append("Rent per hour must be a positive number.")

        # Validate time inputs
        if time_from_str and time_until_str:
            time_format = "%H:%M"
            time_from = datetime.datetime.strptime(time_from_str, time_format).time()
            time_until = datetime.datetime.strptime(time_until_str, time_format).time()

            # Prevent identical start and end times
            if time_from == time_until:
                errors.append("Start and end times cannot be identical.")

        # Case 1: Same day bookings - validate that start time is before end time
        if available_from == available_until:
            if time_from >= time_until:
                errors.append(
                    "For same-day bookings, end time must be after start time"
                )

        # Case 2: Multi-day bookings - any time combination is valid
        # Exception: Identical times might not make practical sense
        elif time_from == time_until:
            # This is optional - remove if you want to allow identical times on different days
            errors.append(
                "Start and end times cannot be identical, even on different days"
            )

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(
                attrs={"min": 1, "max": 5, "class": "form-control"}
            ),
            "comment": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }
