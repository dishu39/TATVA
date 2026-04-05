from django import forms
from .models import Participant, Event


class ParticipantForm(forms.ModelForm):
    events = forms.ModelMultipleChoiceField(
        queryset=Event.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={'required': 'Please select at least one event.'}
    )

    class Meta:
        model = Participant
        fields = ['name', 'email', 'phone', 'college', 'year', 'branch', 'team_name', 'events']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Riya Sharma', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'riya@college.edu', 'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'placeholder': '9876543210', 'maxlength': '15', 'class': 'form-input'}),
            'college': forms.TextInput(attrs={'placeholder': 'IIT Delhi', 'class': 'form-input'}),
            'year': forms.Select(attrs={'class': 'form-input'}),
            'branch': forms.TextInput(attrs={'placeholder': 'Computer Science', 'class': 'form-input'}),
            'team_name': forms.TextInput(attrs={'placeholder': 'Leave blank for solo', 'class': 'form-input'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = Participant.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('A participant with this email is already registered.')
        return email


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'category', 'date', 'venue', 'max_participants', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Hackathon 2025', 'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'venue': forms.TextInput(attrs={'placeholder': 'Seminar Hall A', 'class': 'form-input'}),
            'max_participants': forms.NumberInput(attrs={'placeholder': '100', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-input', 'placeholder': 'Optional details'}),
        }


class CheckinForm(forms.Form):
    reg_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Reg ID (e.g. FEST-0001)',
            'class': 'form-input',
            'autofocus': True,
            'autocomplete': 'off',
        })
    )
