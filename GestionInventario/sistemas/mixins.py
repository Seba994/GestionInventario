# mixins.py (crear este archivo)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

class RolRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin para requerir roles específicos en vistas basadas en clases"""
    roles_permitidos = []
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
            
        if not hasattr(self.request.user, 'personal'):
            return False
            
        user_rol = self.request.user.personal.rol.rol
        return user_rol in self.roles_permitidos or self.request.user.is_superuser
    
    def handle_no_permission(self):
        from django.contrib import messages
        messages.error(self.request, f"No tiene permisos para acceder a esta sección.")
        from django.shortcuts import redirect
        return redirect('principal')

class PermisoRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin para requerir permisos específicos"""
    permiso_requerido = None
    
    def test_func(self):
        if self.permiso_requerido is None:
            raise ValueError("Debe especificar un permiso_requerido")
        
        return (self.request.user.has_perm(self.permiso_requerido) 
                or self.request.user.is_superuser)