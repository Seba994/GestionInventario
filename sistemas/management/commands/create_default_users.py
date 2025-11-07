from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Crea usuarios por defecto: admin, Caro, Seba y Ricardo si no existen.'

    def handle(self, *args, **options):
        User = get_user_model()

        # Usuarios por defecto: admin y dueño (usamos username 'dueno' para evitar problemas con caracteres)
        defaults = [
            {"username": "admin", "email": "admin@example.com", "first_name": "Admin", "is_superuser": True, "is_staff": True},
            {"username": "dueno", "email": "dueno@example.com", "first_name": "Dueño", "is_superuser": True, "is_staff": True},
        ]

        for u in defaults:
            username = u["username"]
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.NOTICE(f"Usuario '{username}' ya existe, se omite."))
                continue

            # Crear usuario sin contraseña (usar set_unusable_password) para obligar a establecerla luego
            user = User(username=username, email=u.get("email", ""))
            user.first_name = u.get("first_name", "")
            if u.get("is_superuser"):
                user.is_superuser = True
                user.is_staff = True
            user.set_unusable_password()
            user.save()

            self.stdout.write(self.style.SUCCESS(f"Usuario '{username}' creado correctamente (sin contraseña)."))

        self.stdout.write(self.style.SUCCESS("Proceso terminado."))
