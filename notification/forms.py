from django import forms


class ThresholdForm(forms.Form):
    threshold = forms.DecimalField(
        label="Low-attendance threshold (%)",
        min_value=0,
        max_value=100,
        decimal_places=1,
        help_text="Students below this percentage in a subject are flagged.",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.5"}),
    )
