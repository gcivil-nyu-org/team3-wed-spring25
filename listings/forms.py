# listings/forms.py
import datetime
from datetime import date
from django import forms
from .models import Listing, Review

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
        available_from = self.cleaned_data.get("available_from")
        if available_from and available_from < date.today():
            raise forms.ValidationError(
                "The 'Available From' date cannot be in the past."
            )
        return available_from

    def clean_available_until(self):
        available_from = self.cleaned_data.get("available_from")
        available_until = self.cleaned_data.get("available_until")

        if available_until and available_until < date.today():
            raise forms.ValidationError(
                "The 'Available Until' date cannot be in the past."
            )

        if available_until and available_from and available_until < available_from:
            raise forms.ValidationError(
                "The 'Available Until' date cannot be before the 'Available From' date."
            )

        return available_until

    def clean(self):
        cleaned_data = super().clean()
        errors = []

        # 1. Check date validation
        available_from = cleaned_data.get("available_from")
        available_until = cleaned_data.get("available_until")
        if available_from and available_until and available_from >= available_until:
            errors.append("Available from date must be before available until date")

        # 2. Check rent validation
        rent_per_hour = cleaned_data.get("rent_per_hour")
        if rent_per_hour is not None and rent_per_hour <= 0:
            errors.append("Rent per hour must be a positive number")

        # 3. Check time validation
        time_from_str = cleaned_data.get("available_time_from")  # e.g. '08:00'
        time_until_str = cleaned_data.get("available_time_until")  # e.g. '12:30'
        if time_from_str and time_until_str:
            time_format = "%H:%M"
            time_from = datetime.datetime.strptime(time_from_str, time_format).time()
            time_until = datetime.datetime.strptime(time_until_str, time_format).time()

            if time_from >= time_until:
                errors.append("Available time from must be before available time until")

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
