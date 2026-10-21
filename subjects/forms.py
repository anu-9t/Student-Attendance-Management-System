from django import forms

from .models import Subject


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["code", "name", "semester"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_code(self):
        return self.cleaned_data["code"].strip().upper()
