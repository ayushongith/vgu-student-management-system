from django import forms
from .models import Attendance


class AttendanceForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    subject = forms.ModelChoiceField(
        queryset=None, widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['subject'].queryset = teacher.subjects.all()
