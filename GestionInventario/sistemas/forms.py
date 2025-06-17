# forms.py
from rest_framework import status
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Personal, Rol , Ubicacion, Consola, Juego, Estado, Clasificacion, Descripcion, Distribucion, Stock, Devolucion
import logging
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

class ModificarRolUsuarioForm(forms.ModelForm):
    class Meta:
        model = Personal 
        fields = ['rol']  
        labels = {
            'rol': 'Rol del Usuario',
        }
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aquí obtenemos la lista de roles disponibles del modelo Rol
        self.fields['rol'].queryset = Rol.objects.all()


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
        fields = ['nombreUbicacion', 'descripcionUbicacion']
        widgets = {
            'nombreUbicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcionUbicacion': forms.TextInput(attrs={'class': 'form-control'}),
        }

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
        fields = ['nombreConsola', 'marcaConsola']
        labels = {
            'nombreConsola': 'Nombre de la Consola',

            'marcaConsola': 'Marca de la Consola'
        }
        widgets = {
            'nombreConsola': forms.TextInput(attrs={'class': 'form-control'}),
            'marcaConsola': forms.TextInput(attrs={'class': 'form-control'}),

        }

    def clean_nombreConsola(self):
        nombre = self.cleaned_data.get('nombreConsola')
        if Consola.objects.filter(nombreConsola__iexact=nombre).exists():
            raise forms.ValidationError("Ya existe una consola con este nombre.")
        return nombre

 
logger = logging.getLogger(__name__)

class JuegoForm(forms.ModelForm):
    class Meta:
        model = Juego
        fields = ['codigoDeBarra', 'nombreJuego', 'consola', 'distribucion', 'clasificacion', 'descripcion', 'imagen']
        labels = {
            "codigoDeBarra": "Código de Barra",
            "nombreJuego": "Nombre del Juego",
            "consola": "Consola",
            "distribucion": "Distribución",
            "clasificacion": "Clasificación",
            "descripcion": "Descripción",
            "imagen": "Imagen"
        }
        widgets = {
            'codigoDeBarra': forms.TextInput(attrs={'class': 'form-control'}),
            'nombreJuego': forms.TextInput(attrs={'class': 'form-control'}),
            'consola': forms.Select(attrs={'class': 'form-select'}),
            'distribucion': forms.Select(attrs={'class': 'form-select'}),
            'clasificacion': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
            
            # Configurar widgets y ordenamiento
            self.fields['descripcion'].queryset = self.fields['descripcion'].queryset.order_by('detallesDescripcion')
            
            # Forzar los IDs para JavaScript
            self.fields['distribucion'].widget.attrs.update({'id': 'id_distribucion'})
            self.fields['clasificacion'].widget.attrs.update({'id': 'id_clasificacion'})
            

            for field in self.fields.values():
                field.widget.attrs['class'] = 'form-control'

            # Filtrar clasificaciones según distribución
            if 'distribucion' in self.data:
                try:
                    distribucion_id = int(self.data.get('distribucion'))
                    self.fields['clasificacion'].queryset = Clasificacion.objects.filter(distribucion_id=distribucion_id)
                except (ValueError, TypeError) as e:
                    logger.error(f"Error procesando distribución: {str(e)}")
                    self.fields['clasificacion'].queryset = Clasificacion.objects.none()
            else:
                self.fields['clasificacion'].queryset = Clasificacion.objects.none()
                
        except Exception as e:
            logger.error(f"Error inicializando formulario: {str(e)}")
            raise ValidationError(
                "Error inicializando el formulario",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def clean_codigoDeBarra(self):
        codigo = self.cleaned_data.get('codigoDeBarra')
        try:
            if codigo:
                if not codigo.isdigit():
                    raise ValidationError(
                        "El código de barra debe contener solo números.",
                        code=status.HTTP_400_BAD_REQUEST
                    )
                    
                existe_codigo = Juego.objects.filter(codigoDeBarra=codigo)
                if self.instance.pk:
                    existe_codigo = existe_codigo.exclude(pk=self.instance.pk)
                if existe_codigo.exists():
                    raise ValidationError(
                        "Este código de barra ya está en uso.",
                        code=status.HTTP_409_CONFLICT
                    )
            return codigo
        except Exception as e:
            logger.error(f"Error validando código de barra: {str(e)}")
            raise ValidationError(
                "Error validando el código de barra",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def clean(self):
        cleaned_data = super().clean()
        try:
            nombre = cleaned_data.get('nombreJuego')
            consola = cleaned_data.get('consola')
            distribucion = cleaned_data.get('distribucion')

            if nombre and consola and distribucion:
                existe = Juego.objects.filter(
                    nombreJuego=nombre,
                    consola=consola,
                    distribucion=distribucion
                )
                if self.instance.pk:
                    existe = existe.exclude(pk=self.instance.pk)

                if existe.exists():
                    raise ValidationError(
                        "Ya existe un juego con ese nombre, consola y distribución.",
                        code=status.HTTP_409_CONFLICT
                    )
            return cleaned_data
        except Exception as e:
            logger.error(f"Error en validación combinada: {str(e)}")
            raise ValidationError(
                "Error validando la combinación del juego",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def save(self, commit=True):
        try:
            juego = super().save(commit=False)
            
            # Asegurar que exista el estado 'Activo'
            estado_activo, created = Estado.objects.get_or_create(
                nombreEstado='Activo',
                defaults={'idEstado': 1}  # Ajusta según tu modelo
            )
            juego.estado = estado_activo
            
            if commit:
                juego.save()
                self.save_m2m()  # Importante para relaciones many-to-many
            
            return juego
            
        except Exception as e:
            logger.error(f"Error guardando juego: {str(e)}")
            raise ValidationError(
                f"Error al guardar el juego: {str(e)}",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )    
class ModificarJuegoForm(forms.ModelForm):
    class Meta:
        model = Juego
        
        fields = '__all__'  
        exclude = ['codigoDeBarra']  # Excluye el campo del formulario
        widgets = {
            'descripcion': forms.Select(attrs={'class': 'form-select'})
        }
        
class FiltroJuegoForm(forms.Form):
    STOCK_CHOICES = [
    ('', 'Todos'),  # valor vacío cuando no se filtra
    ('available', 'Con stock'),
    ('unavailable', 'Sin stock'),
]
    nombre = forms.CharField(required=False)
    
    estado = forms.ModelChoiceField(queryset=Estado.objects.all(), required=False)
    consola = forms.ModelChoiceField(queryset=Consola.objects.all(), required=False)
    clasificacion = forms.ModelChoiceField(queryset=Clasificacion.objects.all(), required=False)
    distribucion = forms.ModelChoiceField(queryset=Distribucion.objects.all(), required=False)
    stock = forms.ChoiceField(choices=STOCK_CHOICES, required=False)

class ModificarPersonalForm(forms.ModelForm):
    nombre = forms.CharField(label='Nombre completo')
    telefono = forms.CharField(max_length=15)
    rol = forms.ModelChoiceField(queryset=Rol.objects.all())

    class Meta:
        model = Personal
        fields = ['nombre', 'telefono', 'rol']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
class CambiarUbicacionForm(forms.Form):
    nueva_ubicacion = forms.ModelChoiceField(
        queryset=Ubicacion.objects.all(),
        label="Nueva Ubicación",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cantidad = forms.IntegerField(
        label="Cantidad a mover",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    motivo = forms.CharField(
        label="Motivo del cambio (opcional)",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ej: Reorganización de inventario'
        })
    )

    def __init__(self, *args, juego=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.juego = juego
        if juego:
            # filtro para excluir ubicaciones que ya tienen stock del juego
            ubicaciones_con_stock = Stock.objects.filter(juego=juego).values_list('ubicacion', flat=True)
            self.fields['nueva_ubicacion'].queryset = Ubicacion.objects.exclude(
                idUbicacion__in=ubicaciones_con_stock
            )


from django import forms
from django.db.models import Q
from .models import Devolucion, Juego, Ubicacion

class DevolucionForm(forms.ModelForm):
    class Meta:
        model = Devolucion
        fields = ['juego', 'cantidad', 'ubicacion_destino', 'motivo']
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ej: Producto defectuoso, cambio de ubicación...'}),
            'juego': forms.Select(attrs={'class': 'select2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar todos los juegos, ordenados por nombre
        self.fields['juego'].queryset = Juego.objects.all().order_by('nombreJuego')
        
        # Mejorar la representación de los juegos en el select
        self.fields['juego'].label_from_instance = lambda obj: (
            f"{obj.nombreJuego} ({obj.consola.nombreConsola}) - "
            f"{'Stock: ' + str(obj.stock_total) if obj.stock_total > 0 else 'Sin stock'}"
        )
        
        # Agregar clases Bootstrap a los campos
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Placeholder para cantidad
        self.fields['cantidad'].widget.attrs['placeholder'] = 'Ej: 1, 2, 5...'
        
        # Ordenar ubicaciones por nombre
        self.fields['ubicacion_destino'].queryset = Ubicacion.objects.all().order_by('nombreUbicacion')

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        if cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a cero")
        return cantidad
        
class ActualizarImagenForm(forms.ModelForm):
    class Meta:
        model = Juego
        fields = ['imagen']
        widgets = {
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['imagen'].required = False