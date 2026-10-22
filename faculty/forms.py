from django import forms

from accounts.models import User

from .models import Faculty


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ["employee_id", "name", "department"]
        labels = {"employee_id": "Employee ID"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_employee_id(self):
        return self.cleaned_data["employee_id"].strip().upper()


class NewFacultyForm(FacultyForm):
    """Adding a faculty member also creates their login."""

    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(
        label="Initial password", min_length=8, widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        faculty = super().save(commit=False)
        faculty.user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"],
            role=User.Role.FACULTY,
        )
        if commit:
            faculty.save()
        return faculty
