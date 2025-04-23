from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import PersonalForm, RolForm
from .models import Personal

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

