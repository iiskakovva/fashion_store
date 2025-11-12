from django import forms

class UserPreferencesForm(forms.Form):
    THEME_CHOICES = [
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ru', 'Russian'),
        ('es', 'Spanish'),
    ]
    
    favorite_styles = forms.MultipleChoiceField(
        choices=[
            ('casual', 'Casual'),
            ('formal', 'Formal'),
            ('sport', 'Sport'),
            ('vintage', 'Vintage'),
            ('bohemian', 'Bohemian'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    preferred_sizes = forms.MultipleChoiceField(
        choices=[
            ('xs', 'XS'),
            ('s', 'S'),
            ('m', 'M'),
            ('l', 'L'),
            ('xl', 'XL'),
            ('xxl', 'XXL'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    theme = forms.ChoiceField(
        choices=THEME_CHOICES,
        widget=forms.RadioSelect,
        required=False
    )
    
    language = forms.ChoiceField(
        choices=LANGUAGE_CHOICES,
        widget=forms.RadioSelect,
        required=False
    )