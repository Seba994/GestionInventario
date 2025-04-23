# forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Personal, Rol

class PersonalForm(UserCreationForm):
    
    nombre = forms.CharField(label='Nombre completo')
    rol = forms.ModelChoiceField(queryset=Personal._meta.get_field('rol').related_model.objects.all())
    telefono = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'nombre', 'rol', 'telefono']

    def save(self, commit=True):
        user = super().save(commit)
        personal = Personal(
            nombre=self.cleaned_data['nombre'],
            rol=self.cleaned_data['rol'],
            telefono=self.cleaned_data['telefono'],
            usuario=user
        )
        if commit:
            personal.save()
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'



class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = ['rol']
        labels = {
            'rol': 'Nombre del Rol',
        }
        widgets = {
            'rol': forms.TextInput(attrs={'class': 'form-control'}),
        }