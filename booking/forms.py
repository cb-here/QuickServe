from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'time_slot', 'address', 'duration', 'total_price']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'time_slot': forms.Select(choices=[('9:00 AM', '9:00 AM'), ('11:00 AM', '11:00 AM'), ('1:00 PM', '1:00 PM'), ('3:00 PM', '3:00 PM'), ('5:00PM', '5:00PM'), ('7:00PM', '7:00PM')]),
            'total_price': forms.HiddenInput(),
        }
        
    def clean_total_price(self):
        total_price = self.cleaned_data.get('total_price')
        if total_price is None or total_price <= 0:
            raise forms.ValidationError("Total price must be greater than zero.")
        return total_price
    
class RatingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['rating']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)]),
        }