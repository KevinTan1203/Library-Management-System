from django import forms
from library_system.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"
