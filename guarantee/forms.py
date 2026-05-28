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
class ActiveGuratanteeSerialNumberSearch(forms.Form):
    active_seria_number = forms.CharField(
        required=True, 
        widget=forms.TextInput(
            attrs={
                'class': 'tailwind-input',
                'placeholder':' شماره سریال گارانتی فعال شده '
            }
        )
    )