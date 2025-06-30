from django import forms
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget


class BlogFilterForm(forms.Form):

    end_date = JalaliDateField(
        label="تا تاریخ",
        widget=AdminJalaliDateWidget(
            attrs={
                "class": "tailwind-input w-full",
                "placeholder": "تا تاریخ",
            }
        ),
        required=False,
    )
    start_date = JalaliDateField(
        label="از تاریخ",
        widget=AdminJalaliDateWidget(
            attrs={
                "class": "tailwind-input w-full",
                "placeholder": "از تاریخ",
            }
        ),
        required=False,
    )
