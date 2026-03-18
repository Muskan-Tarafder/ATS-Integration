from django import forms


class ApplicationForm(forms.Form):
    name = forms.CharField(
        label="Full Name",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Abhinav M'}),
        help_text="Enter your first and last name."
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'placeholder': 'name@example.com'})
    )
    phone = forms.CharField(
        label="Phone Number",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+91 98765 43210'})
    )
    resume_url = forms.URLField(
        label="Resume URL",
        widget=forms.URLInput(attrs={'placeholder': 'https://drive.google.com/...'}),
        help_text="Provide a public link to your resume (Drive, Dropbox, etc.)"
    )