# booking/forms.py
import datetime
from django import forms
from .models import Booking

# Generate half-hour choices for 00:00 -> 23:30
HALF_HOUR_CHOICES = [
    (f"{hour:02d}:{minute:02d}", f"{hour:02d}:{minute:02d}")
    for hour in range(24)
    for minute in (0, 30)
]

class BookingForm(forms.ModelForm):
    # Use ChoiceFields for half-hour increments
    start_time = forms.ChoiceField(choices=HALF_HOUR_CHOICES, label="Start Time")
    end_time = forms.ChoiceField(choices=HALF_HOUR_CHOICES, label="End Time")

    class Meta:
        model = Booking
        fields = ["booking_date", "start_time", "end_time"]
        widgets = {
            "booking_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        # Pop the listing object if provided
        listing = kwargs.pop("listing", None)
        super().__init__(*args, **kwargs)

        if listing:
            min_time = listing.available_time_from  # e.g., datetime.time(8, 0)
            max_time = listing.available_time_until # e.g., datetime.time(18, 30)

            # Build valid half-hour choices within the listing's available time range.
            valid_choices = []
            for hour in range(24):
                for minute in (0, 30):
                    t = datetime.time(hour, minute)
                    if min_time <= t <= max_time:
                        t_str = f"{hour:02d}:{minute:02d}"
                        valid_choices.append((t_str, t_str))
            self.fields["start_time"].choices = valid_choices
            self.fields["end_time"].choices = valid_choices

    def clean(self):
        cleaned_data = super().clean()
        errors = []

        start_time_str = cleaned_data.get("start_time")
        end_time_str = cleaned_data.get("end_time")
        if start_time_str and end_time_str:
            time_format = "%H:%M"
            try:
                # Convert the string times to datetime.time objects
                start_time = datetime.datetime.strptime(start_time_str, time_format).time()
                end_time = datetime.datetime.strptime(end_time_str, time_format).time()
            except ValueError:
                errors.append("Invalid time format.")
                raise forms.ValidationError(errors)

            if start_time >= end_time:
                errors.append("Start Time must be before End Time")

            # Assign the converted time objects back to cleaned_data
            cleaned_data["start_time"] = start_time
            cleaned_data["end_time"] = end_time

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data
