# blog/forms.py
from django import forms
from .models import Comment, Subscriber # Ensure Subscriber is imported


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body') # Fields for the user to fill
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name (optional if logged in)'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your Email (optional, not shown publicly)'}),
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comment...'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) # Get user if passed
        super().__init__(*args, **kwargs)
        if self.user and self.user.is_authenticated:
            # If user is logged in, name and email are not required and can be hidden or pre-filled
            self.fields['name'].required = False
            self.fields['email'].required = False
            # Optionally, hide them or prefill them:
            # self.fields['name'].widget = forms.HiddenInput()
            # self.fields['email'].widget = forms.HiddenInput()
            # self.initial['name'] = self.user.get_full_name() or self.user.username
            # self.initial['email'] = self.user.email



class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Your Email Address'}))
    subject = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Your Message'}))

class NewsletterSubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscriber # Changed to string reference to resolve NameError
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email address', 'aria-label': 'Email for newsletter'}),
        }

