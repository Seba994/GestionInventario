from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .models import Personal

"""
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
    
"""
# decorators.py (mejorado)
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def rol_requerido(*roles_permitidos):
    """
    Decorador que verifica si el usuario tiene alguno de los roles requeridos
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Debe iniciar sesión para acceder a esta página.")
                return redirect('login')
            
            # Verificar si el usuario tiene personal asociado
            if not hasattr(request.user, 'personal'):
                messages.error(request, "No tiene un perfil de personal asignado.")
                return redirect('login')
            
            # Verificar si el usuario tiene alguno de los roles permitidos o es superusuario
            user_rol = request.user.personal.rol.rol.lower()
            roles_permitidos_lower = [rol.lower() for rol in roles_permitidos]
            
            if user_rol in roles_permitidos_lower or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                # Mensaje más específico según el rol del usuario
                if user_rol == 'bodeguero':
                    messages.error(request, "❌ Los bodegueros no tienen permisos para gestionar usuarios. Solo pueden gestionar inventario y stock.")
                elif user_rol == 'locatario':
                    messages.error(request, "❌ Los locatarios solo tienen permisos de visualización. No pueden realizar modificaciones.")
                else:
                    messages.error(request, f"❌ No tiene permisos para acceder a esta sección. Se requiere uno de estos roles: {', '.join(roles_permitidos)}")
                
                return redirect('inicio')
        return _wrapped_view
    return decorator