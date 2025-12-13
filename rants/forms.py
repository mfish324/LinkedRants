from django import forms
from .models import Rant, SideBySide, Category


class RantForm(forms.ModelForm):
    """Form for submitting a new rant."""

    class Meta:
        model = Rant
        fields = ['title', 'body', 'category', 'is_anonymous', 'display_name', 'email']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Optional title for your rant...',
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Let it all out... (Markdown supported)',
                'rows': 8,
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your name (only shown if not anonymous)',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Optional - for notifications if featured',
            }),
        }
        labels = {
            'is_anonymous': 'Post anonymously',
            'display_name': 'Display name',
            'email': 'Email (optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Select a category..."

    def clean(self):
        cleaned_data = super().clean()
        is_anonymous = cleaned_data.get('is_anonymous')
        display_name = cleaned_data.get('display_name')

        # If not anonymous, encourage a display name
        if not is_anonymous and not display_name:
            cleaned_data['is_anonymous'] = True

        return cleaned_data


class SideBySideForm(forms.ModelForm):
    """Form for submitting a LinkedIn vs Reality comparison."""

    class Meta:
        model = SideBySide
        fields = ['context', 'linkedin_version', 'reality_version', 'is_anonymous', 'display_name', 'email']
        widgets = {
            'context': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Brief context (e.g., "After getting laid off")',
            }),
            'linkedin_version': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'The LinkedIn Version: What you posted (or would post)...',
                'rows': 6,
            }),
            'reality_version': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'The Reality: What actually happened...',
                'rows': 6,
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your name (only shown if not anonymous)',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Optional - for notifications if featured',
            }),
        }
        labels = {
            'context': 'Context',
            'linkedin_version': 'The LinkedIn Version',
            'reality_version': 'The Reality',
            'is_anonymous': 'Post anonymously',
            'display_name': 'Display name',
            'email': 'Email (optional)',
        }

    def clean(self):
        cleaned_data = super().clean()
        is_anonymous = cleaned_data.get('is_anonymous')
        display_name = cleaned_data.get('display_name')

        if not is_anonymous and not display_name:
            cleaned_data['is_anonymous'] = True

        return cleaned_data


class ReportForm(forms.Form):
    """Simple form for reporting content."""
    REASON_CHOICES = [
        ('spam', 'Spam or advertising'),
        ('hate', 'Hate speech or discrimination'),
        ('doxxing', 'Contains personal information'),
        ('threats', 'Threats or harassment'),
        ('other', 'Other'),
    ]

    reason = forms.ChoiceField(
        choices=REASON_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-radio'}),
        label='Reason for report'
    )
    details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'placeholder': 'Additional details (optional)',
            'rows': 3,
        }),
        label='Additional details'
    )
