from django import forms
from django.core.exceptions import ValidationError
from .models import Employee

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'role', 'skills', 'is_available', 'working_hours_start',
            'working_hours_end', 'phone_number', 'email', 'address',
            'profile_picture', 'experience_years', 'hourly_rate', 'is_verified'
        ]
        exclude = ['user', 'average_rating', 'total_reviews'] 
        widgets = {
            'working_hours_start': forms.TimeInput(attrs={'type': 'time'}),
            'working_hours_end': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        user = self.instance.user
        if Employee.objects.filter(user=user).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This user already has an employee record.")
    
        return cleaned_data

