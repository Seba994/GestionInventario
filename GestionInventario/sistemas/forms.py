# forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Personal, Rol , Ubicacion, Consola, Juego 

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

# Formulario para Ubicacion, con nombre unico
class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = '__all__'

    def clean_nombreUbicacion(self):
        nombre = self.cleaned_data.get('nombreUbicacion')
        if Ubicacion.objects.filter(nombreUbicacion__iexact=nombre).exists():
            raise forms.ValidationError("Ya existe una ubicación con este nombre.")
        return nombre

# Formulario para Consola, con nombre unico

class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = '__all__'

    def clean_nombreUbicacion(self):
        nombre = self.cleaned_data.get('nombreUbicacion')
        if Ubicacion.objects.filter(nombreUbicacion__iexact=nombre).exists():
            raise forms.ValidationError("Ya existe una ubicación con este nombre.")
        return nombre

# Formulario para Consola
class ConsolaForm(forms.ModelForm):
    class Meta:
        model = Consola
        fields = '__all__'

    def clean_nombreConsola(self):
        nombre = self.cleaned_data.get('nombreConsola')
        if Consola.objects.filter(nombreConsola__iexact=nombre).exists():
            raise forms.ValidationError("Ya existe una consola con este nombre.")
        return nombre

#formulario para juegos, con validaciones
class JuegoForm(forms.ModelForm):
    class Meta:
        model = Juego
        exclude = ['unidades']

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombreJuego')
        consola = cleaned_data.get('consola')
        distribucion = cleaned_data.get('distribucion')
        codigo = cleaned_data.get('codigoDeBarra')

        # Validar combinación lógica
        if nombre and consola and distribucion:
            existe = Juego.objects.filter(
                nombreJuego=nombre,
                consola=consola,
                distribucion=distribucion
            )
            if self.instance.pk:
                existe = existe.exclude(pk=self.instance.pk)

            if existe.exists():
                raise forms.ValidationError(
                    "Ya existe un juego con ese nombre, consola y distribución."
                )

        # Validar código de barra duplicado
        if codigo is not None:
            existe_codigo = Juego.objects.filter(codigoDeBarra=codigo)
            if self.instance.pk:
                existe_codigo = existe_codigo.exclude(pk=self.instance.pk)

            if existe_codigo.exists():
                self.add_error('codigoDeBarra', "Este código de barra ya está en uso.")

        return cleaned_data
    
from django import forms
from .models import Juego  # Asegúrate de importar tu modelo de producto

class ModificarJuegoForm(forms.ModelForm):
    class Meta:
        model = Juego
        fields = '__all__'  
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }