from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .models import Personal

def rol_requerido(rol_nombre):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            try:
                personal = Personal.objects.get(usuario=request.user)
                if personal.rol.rol.lower() == rol_nombre.lower():
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, "No tienes permisos para acceder a esta sección.")
                    return redirect('inicio')
            except Personal.DoesNotExist:
                messages.error(request, "No tienes un perfil asociado.")
                return redirect('inicio')
        return _wrapped_view
    return decorator