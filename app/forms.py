from django import forms
from app.models import *
from django.forms import ModelChoiceField, modelformset_factory


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.nome


class FeriasForm(forms.ModelForm):
    class Meta:
        model = Ferias
        fields = "__all__"
        widgets = {
            'data_inicio': forms.TextInput(attrs={'id':'ferias_datepicker', 'class': 'datepicker', 'autocomplete': 'off'}),
        }
        field_classes = {
            'trabalhador': MyModelChoiceField,
        }


class LicencaPremioForm(forms.ModelForm):
    class Meta:
        model = LicencaPremio
        fields = "__all__"
        widgets = {'data_inicio': forms.TextInput(attrs={'id':'licenca_datepicker', 'class': 'datepicker', 'autocomplete': 'off'})}
        field_classes = {
            'trabalhador': MyModelChoiceField,
        }


class AbonoForm(forms.ModelForm):
    class Meta:
        model = Abono
        fields = "__all__"
        widgets = {
            'data': forms.TextInput(
                attrs={
                    'id':'abono_datepicker',
                    'class': 'datepicker',
                    'autocomplete': 'off',
                    'data-mask': '12/22/1978',
                }
            )
        }
        field_classes = {
            'trabalhador': MyModelChoiceField,
        }


class TrabalhadorForm(forms.ModelForm):
    class Meta:
        model = Trabalhador
        fields = '__all__'
        widgets = {
            'data_admissao': forms.TextInput(attrs={
                'class': 'datepicker2',
                'autocomplete': 'off',
            }),
        }
        field_classes = {
            'setor': MyModelChoiceField,
        }


class TrabalhadorFormSemAdmissao(forms.ModelForm):
    class Meta:
        model = Trabalhador
        exclude = ['data_admissao', ]
        widgets = {'data_admissao': forms.TextInput(attrs={'id':'trabalhador_datepicker', 'class': 'datepicker2', 'autocomplete': 'off'})}
        field_classes = {
            'setor': MyModelChoiceField,
        }


class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = "__all__"


class LoginForm(forms.Form):
    usuario = forms.CharField(max_length=200, strip=True, label='', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Seu nome de usuário',
        'type': 'text',
        'autocomplete': 'off',
    }))
    senha = forms.CharField(label='', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Sua senha',
        'type': 'password'
    }))


class AutorizacaoForm(forms.Form):
    trabalhador = MyModelChoiceField(queryset=Trabalhador.objects.all(), widget=forms.Select(attrs={
        'name': 'trabalhador_id',
    }))

