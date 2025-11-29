from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Personal, Rol

# Personalizar nombres en plural
Personal._meta.verbose_name_plural = "Personal"
Rol._meta.verbose_name = "Rol"
Rol._meta.verbose_name_plural = "Roles"

class PersonalInline(admin.StackedInline):
    model = Personal
    can_delete = True
    verbose_name = 'Información de Personal'
    verbose_name_plural = 'Información de Personal'

class CustomUserAdmin(UserAdmin):
    inlines = (PersonalInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_rol')
    
    def get_rol(self, obj):
        try:
            return obj.personal.rol
        except Personal.DoesNotExist:
            return '-'
    get_rol.short_description = 'Rol'

class PersonalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rol', 'telefono', 'usuario')
    list_filter = ('rol',)
    search_fields = ('nombre', 'usuario__username')

class RolAdmin(admin.ModelAdmin):
    list_display = ('rol',)
    search_fields = ('rol',)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Personal, PersonalAdmin)
admin.site.register(Rol, RolAdmin)
