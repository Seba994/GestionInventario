"""
funciones utilitarias para el sistema de inventario
"""
from django.db.models import Sum
from .models import Stock
from django.conf import settings

def calcular_stock(juego):
    """
    Calcula el stock total de un juego específico.
    """
    return Stock.objects.filter(juego=juego).aggregate(
        total=Sum('cantidad')
    )['total'] or 0
    
def delete_image_from_supabase(image_url: str):
    """
    Recibe la URL pública y elimina el archivo del bucket.
    """
    if not image_url:
        return

    client = settings.SUPABASE_CLIENT
    bucket = settings.SUPABASE_BUCKET_NAME

    # El URL termina en /bucket_name/path
    # Ejemplo: .../object/public/gestionInventario/juegos/123.png
    try:
        path = image_url.split(f"{bucket}/")[1]
    except:
        return

    client.storage.from_(bucket).remove([path])

import uuid
from django.conf import settings

def upload_image_to_supabase(file_obj, carpeta="juegos"):
    client = settings.SUPABASE_CLIENT
    bucket = settings.SUPABASE_BUCKET_NAME

    # Crear nombre único
    extension = file_obj.name.split('.')[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    path = f"{carpeta}/{filename}"

    upload = client.storage.from_(bucket).upload(
        path,
        file_obj,
        {"content-type": file_obj.content_type}
    )

    if upload.get("error"):
        return None

    # Obtener URL pública
    public_url = client.storage.from_(bucket).get_public_url(path)
    return public_url
