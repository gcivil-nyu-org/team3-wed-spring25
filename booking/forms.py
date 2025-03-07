import datetime
from django import forms
from .models import Booking
from datetime import date


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["booking_date", "start_time", "end_time"]
        widgets = {
            "booking_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.listing = kwargs.pop("listing", None)  # Store listing in self
        self.user = kwargs.pop("user", None)  # Store user in self
        super(BookingForm, self).__init__(*args, **kwargs)  # Call parent constructor

    def clean_booking_date(self):
        booking_date = self.cleaned_data.get("booking_date")
        if booking_date and booking_date < date.today():
            raise forms.ValidationError("You cannot book a listing for a past date.")
        return booking_date


def clean(self):
    cleaned_data = super().clean()
    errors = []

    start_time = cleaned_data.get("start_time")
    end_time = cleaned_data.get("end_time")

    # Ensure start_time and end_time exist and are strings before parsing
    if isinstance(start_time, str) and isinstance(end_time, str):
        time_format = "%H:%M"
        try:
            start_time = datetime.datetime.strptime(start_time, time_format).time()
            end_time = datetime.datetime.strptime(end_time, time_format).time()
        except ValueError:
            errors.append("Invalid time format.")
            raise forms.ValidationError(errors)

        # Store the converted time objects back in cleaned_data
        cleaned_data["start_time"] = start_time
        cleaned_data["end_time"] = end_time

    # Ensure start time is before end time
    if start_time and end_time and start_time >= end_time:
        errors.append("Start Time must be before End Time")

    # ✅ Fix: Prevent booking own listing
    if hasattr(self, "listing") and hasattr(self, "user"):
        if self.listing and self.user and self.listing.owner == self.user:
            errors.append("You cannot book your own listing.")

    if errors:
        raise forms.ValidationError(errors)

    return cleaned_data
