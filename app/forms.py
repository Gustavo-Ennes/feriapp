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
            'rg': forms.TextInput(attrs={
                'class': 'rg',
                'autocomplete': 'off',
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'cpf',
                'autocomplete': 'off',
            }),
            'ctps': forms.TextInput(attrs={
                'class': 'ctps',
                'autocomplete': 'off',
            }),
            'ctps_serie': forms.TextInput(attrs={
                'class': 'ctps_serie',
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


class ConfForm(forms.ModelForm):
    class Meta:
        model = Conf
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


class AtestadoForm(forms.Form):
    trabalhador = MyModelChoiceField(queryset=Trabalhador.objects.all(), widget=forms.Select(attrs={
        'name': 'trabalhador_id',
    }))
    rg = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'class': 'rg',
            }
        )
    )
    cpf = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'class': 'cpf',
            }
        )
    )
    ctps = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'class': 'ctps',
            }
        )
    )
    ctps_serie = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'class': 'ctps-serie',
            }
        )
    )


class AvisoForm(forms.Form):
    opcoes_tipo = [
        ['alerta', "Alerta"],
        ['info', 'Informativo'],
        ['urgencia', "Urgência"],
        ['proibicao', "Proibição"],
    ]
    opcoes_pagina = [
        ['r', "Retrato"],
        ['p', 'Paisagem']
    ]
    orientacao = forms.ChoiceField(choices=opcoes_pagina, label='Orientação da página')
    tipo = forms.ChoiceField(choices=opcoes_tipo)
    titulo = forms.CharField(max_length=200, label="Título")
    conteudo = forms.CharField(widget=forms.Textarea(), label="Conteúdo")
    observacoes = forms.CharField(required=False, widget=forms.Textarea(), label="Observações")
