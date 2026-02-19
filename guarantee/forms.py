from django import forms

class GuratanteeSerialNumberSearch(forms.Form):
    seria_number = forms.CharField(
        required=True, 
        widget=forms.TextInput(
            attrs={
                'class': 'tailwind-input',
                'placeholder':'شماره سریال محصول'
            }
        )
    )