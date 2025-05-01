from django import forms
from .models import Wholesaler

class WholesalerForm(forms.ModelForm):
    class Meta:
        model = Wholesaler
        fields = ['name']
