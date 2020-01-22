from django import forms
from app.models import *

class FeriasForm(forms.ModelForm):
    class Meta:
        model = Ferias
        fields = "__all__"
        widgets={'data_inicio': forms.TextInput(attrs={'class': 'datepicker', 'autocomplete' : 'off'})}


class LicencaPremioForm(forms.ModelForm):
    class Meta:
        model = LicencaPremio
        fields = "__all__"
        widgets={'data_inicio': forms.TextInput(attrs={'class': 'datepicker', 'autocomplete' : 'off'})}


class AbonoForm(forms.ModelForm):
    class Meta:
        model = Abono
        fields = "__all__"
        widgets={'data': forms.TextInput(attrs={'class': 'datepicker', 'autocomplete' : 'off'})}


class TrabalhadorForm(forms.ModelForm):
    class Meta:
        model = Trabalhador
        fields = "__all__"
        widgets={'data_admissao': forms.TextInput(attrs={'class': 'datepicker_admissao', 'autocomplete' : 'off'})}


class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = "__all__"



class LoginForm(forms.Form):
	usuario = forms.CharField(max_length=200, strip=True,label='', widget=forms.TextInput(attrs={
		'class' : 'form-control',
		'placeholder' : 'Seu nome de usuário',
		'type' : 'text',
	}))
	senha = forms.CharField(label='', widget=forms.PasswordInput(attrs={
		'class' : 'form-control',
		'placeholder' : 'Sua senha',
		'type' : 'password'
	}))
