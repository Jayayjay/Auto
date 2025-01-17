from django import forms
from .models import IDCard

class IDCardForm(forms.ModelForm):
    class Meta:
        model = IDCard
        fields = ['name', 'mat_number', 'department', 'gender', 'blood_group', 'passport', 'signature']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'mat_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Matric Number'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Department'}),
            'gender': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter your Gender'}),
            'blood_group': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter your Blood Group'}),
            'passport': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'signature': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }