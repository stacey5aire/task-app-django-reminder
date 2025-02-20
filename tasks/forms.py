from django import forms
from .models import Task  # Import your Task model

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "scheduled_date", "reminder", "completed"]
        widgets = {
            "scheduled_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "reminder": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


from django import forms
from .models import Profile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["image"]
