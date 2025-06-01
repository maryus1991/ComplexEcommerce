from django import forms
from django.core.exceptions import ValidationError
from .models import ProductComment

class ProductCommentForm(forms.ModelForm):
    class Meta:
        model = ProductComment
        fields = ['subject', 'comment', 'suggest_product']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'tailwind-input', 'placeholder':"عنوان"}),
            'comment': forms.Textarea(attrs={'class': 'h-24 tailwind-input', 'placeholder':"متن دیدگاه"}),
            'suggest_product': forms.HiddenInput(attrs={'id': 'suggest_product_hidden_input'}),
        }


    def clean_suggest_product(self):
        value = self.cleaned_data['suggest_product']

        if value in [True, False]:
            return value
        raise ValidationError('field should be True or False')
