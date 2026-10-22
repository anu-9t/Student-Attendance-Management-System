from django import forms

from faculty.models import Faculty

from .models import Subject, SubjectAssignment, TimeSlot


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


class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ["label", "start_time", "end_time"]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }
        help_texts = {"label": "For example: Period 1"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = SubjectAssignment
        fields = ["faculty", "subject", "class_group"]
        labels = {"class_group": "Class"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["faculty"].queryset = Faculty.objects.filter(is_active=True)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-select"
