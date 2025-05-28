from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import PersonalForm, RolForm, ConsolaForm, UbicacionForm, JuegoForm
from .models import Personal, Consola, Ubicacion, Juego, Clasificacion
from django.http import JsonResponse
from django.contrib import messages

def crear_personal(request):
    if request.method == 'POST':
        form = PersonalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_usuarios')  # Asegúrate que esa URL esté definida
    else:
        form = PersonalForm()

    usuario_logeado = Personal.objects.get(usuario=request.user)
    
    data_user = {
        'is_authenticated': True,
        'role': usuario_logeado.rol.rol,
        'get_full_name': usuario_logeado.nombre,
        'username' : usuario_logeado.usuario
    }

    return render(request, 'Registros/crear_personal.html', 
                  {'form': form, 'user':data_user})

def crear_rol(request):
    if request.method == 'POST':
        form = RolForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = RolForm()
    return render(request, 'Registros/crear_rol.html', {'form': form})


from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def gestion_usuarios(request):
    usuarios_data = []

    for user in User.objects.all():
        try:
            personal = Personal.objects.get(usuario=user)
            usuarios_data.append({
                'nombre': personal.nombre,
                'rol': personal.rol.rol,
                'usuario': user.username,
                'telefono': personal.telefono,
                'estado': user.is_active,
                'ultimo_ingreso': user.last_login,
            })
        except Personal.DoesNotExist:
            continue
    
    usuario_logeado = Personal.objects.get(usuario=request.user)
    
    data_user = {
        'is_authenticated': True,
        'role': usuario_logeado.rol.rol,
        'get_full_name': usuario_logeado.nombre,
        'username' : usuario_logeado.usuario
    }

    return render(request, 'usuarios/gestion_usuarios.html', {
        'usuarios': usuarios_data,
        'user': data_user
    })

# Vista para registrar nuevas consolas
def registrar_consola(request):
    if request.method == 'POST':
        form = ConsolaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "La consola se ha registrado correctamente.")
            return redirect('registrar_consola')
    else:
        form = ConsolaForm()
    return render(request, 'Registros/registrar_consolas.html', {'form': form})


# Vista para listar consolas
def lista_consolas(request):
    consolas = Consola.objects.all()
    return render(request, 'consolas/lista.html', {'consolas': consolas})

# Vista para registrar nuevas ubicación
def registrar_ubicacion(request):
    if request.method == 'POST':
        form = UbicacionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_ubicaciones')
    else:
        form = UbicacionForm()
    return render(request, 'ubicaciones/registrar.html', {'form': form})

# Vista para listar ubicaciones
def lista_ubicaciones(request):
    ubicaciones = Ubicacion.objects.all()
    return render(request, 'ubicaciones/lista.html', {'ubicaciones': ubicaciones})

# Vista para registrar juego
@login_required(login_url='login')
def registrar_juego(request):
    if request.method == 'POST':
        form = JuegoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_juegos')
    else:
        form = JuegoForm()
    return render(request, 'Registros/registrar_juego.html', {'form': form})

# Vista para listar juegos
def lista_juegos(request):
    juegos = Juego.objects.all()
    return render(request, 'juegos/lista.html', {'juegos': juegos})

def obtener_clasificaciones(request):
    distribucion_id = request.GET.get('distribucion_id')
    clasificaciones = Clasificacion.objects.filter(distribucion_id=distribucion_id).values('idClasificacion', 'descripcionClasificacion')
    return JsonResponse(list(clasificaciones), safe=False)