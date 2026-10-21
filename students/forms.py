from django import forms

from accounts.models import User

from .models import ClassGroup, Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["srn", "name", "email", "class_group"]
        labels = {"srn": "SRN", "class_group": "Class"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["class_group"].queryset = ClassGroup.objects.all()
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["class_group"].widget.attrs["class"] = "form-select"

    def clean_srn(self):
        return self.cleaned_data["srn"].strip().upper()


class NewStudentForm(StudentForm):
    """Adding a student also creates their login. The username is the SRN."""

    password = forms.CharField(
        label="Initial password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        min_length=8,
        help_text="The student logs in with their SRN and this password.",
    )

    def clean_srn(self):
        srn = super().clean_srn()
        if User.objects.filter(username__iexact=srn).exists():
            raise forms.ValidationError("A login with this SRN already exists.")
        return srn

    def save(self, commit=True):
        student = super().save(commit=False)
        user = User.objects.create_user(
            username=student.srn,
            password=self.cleaned_data["password"],
            email=student.email,
            role=User.Role.STUDENT,
        )
        student.user = user
        if commit:
            student.save()
        return student
