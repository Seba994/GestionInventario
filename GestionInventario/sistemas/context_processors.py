# context_processors.py
def user_roles(request):
    if request.user.is_authenticated and hasattr(request.user, 'personal'):
        user_rol = request.user.personal.rol.rol.lower()
        return {
            'user_rol': user_rol,
            'is_dueño': user_rol == 'dueño',
            'is_bodeguero': user_rol == 'bodeguero', 
            'is_locatario': user_rol == 'locatario',
            'puede_administrar_usuarios': user_rol == 'dueño',
            'puede_gestionar_stock': user_rol in ['dueño', 'bodeguero'],
            'puede_modificar_inventario': user_rol in ['dueño', 'bodeguero'],
            'puede_ver_reportes': user_rol == 'dueño',  # SOLO dueño ve reportes
        }
    return {}