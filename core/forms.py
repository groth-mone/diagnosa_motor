from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Gejala, Diagnosa, Rule

class GejalaForm(forms.ModelForm):
    class Meta:
        model = Gejala
        fields = ['kode', 'nama']

class DiagnosaForm(forms.ModelForm):
    class Meta:
        model = Diagnosa
        fields = ['kode', 'nama', 'solusi']

class RuleForm(forms.ModelForm):
    gejala = forms.ModelMultipleChoiceField(
        queryset=Gejala.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Rule
        fields = ['diagnosa']

    def save(self, commit=True):
        rule = super().save(commit=False)
        gejala_ids = self.cleaned_data['gejala']
        rule.gejala_ids = ",".join(str(g.id) for g in gejala_ids)
        if commit:
            rule.save()
        return rule
    
class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login']