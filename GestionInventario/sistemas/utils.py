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
    
from supabase import create_client, Client
from django.conf import settings
import os

SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_image_to_supabase(file_obj, file_name, bucket='gestionInventario'):
    try:
        # leer contenido
        file_data = file_obj.read()
        file_obj.seek(0)
        content_type = getattr(file_obj, 'content_type', 'application/octet-stream')

        # subir
        supabase.storage.from_(bucket).upload(path=file_name, file=file_data, file_options={"content-type": content_type})

        # obtener url pública (manejar distintos retornos)
        pub = supabase.storage.from_(bucket).get_public_url(file_name)
        public_url = pub.get('publicURL') if isinstance(pub, dict) else pub

        return {"success": True, "path": public_url}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_image_from_supabase(path_or_name, bucket='gestionInventario'):
    try:
        # si se pasa una URL, extraer nombre del archivo
        name = os.path.basename(path_or_name)
        result = supabase.storage.from_(bucket).remove([name])
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def upload_or_replace_game_image(juego, file_obj, file_name, bucket='gestionInventario'):
    # eliminar previa si existe (no detener por error)
    try:
        if getattr(juego, 'imagen', None):
            _ = delete_image_from_supabase(juego.imagen, bucket=bucket)
    except Exception:
        pass

    resultado = upload_image_to_supabase(file_obj, file_name, bucket=bucket)
    if not resultado.get("success"):
        raise Exception(resultado.get("error") or "Error subiendo imagen")

    # guardar URL en el modelo juego (ajustar campo si en tu modelo no se llama 'imagen')
    juego.imagen = resultado["path"]
    juego.save(update_fields=['imagen'])
    return resultado["path"]