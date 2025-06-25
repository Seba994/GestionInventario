"""
funciones utilitarias para el sistema de inventario
"""
import re
import os
import time
from django.db.models import Sum
from .models import Stock,  Ubicacion
from GestionInventario.settings import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

# Inicializar el cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def calcular_stock(juego):
    """
    Calcula el stock total de un juego específico.
    """
    return Stock.objects.filter(juego=juego).aggregate(
        total=Sum('cantidad')
    )['total'] or 0

def buscar_ubicaciones(termino):
    """Busca ubicaciones por nombre"""
    if termino:
        return Ubicacion.objects.filter(nombreUbicacion__icontains=termino)
    return Ubicacion.objects.all()

def sanitize_filename(filename):
    """Limpia el nombre del archivo de caracteres especiales y espacios"""
    # Obtener nombre y extensión
    name, ext = os.path.splitext(filename)
    
    # Convertir a minúsculas y reemplazar caracteres no deseados
    name = name.lower()
    # Reemplazar espacios y caracteres especiales con guión bajo
    name = re.sub(r'[\s]+', '_', name)  # Primero reemplazar espacios
    name = re.sub(r'[^a-z0-9_]', '_', name)  # Luego otros caracteres especiales
    # Eliminar guiones bajos múltiples
    name = re.sub(r'_+', '_', name)
    # Eliminar guiones al inicio y final
    name = name.strip('_')
    
    # Generar nombre único para evitar colisiones
    timestamp = str(int(time.time()))
    return f"{timestamp}_{name}{ext.lower()}"

def upload_image_to_supabase(file_obj, file_name, bucket='img-juegos'):
    """Sube imagen a Supabase y devuelve la URL pública"""
    try:
        # Lee el archivo en memoria
        file_data = file_obj.read()
        file_obj.seek(0)
        # Sube el archivo a Supabase
        response = supabase.storage.from_(bucket).upload(
            path=file_name,
            file=file_data,
            file_options={"content-type": file_obj.content_type}
        )
        # Obtener la URL pública
        public_url = supabase.storage.from_(bucket).get_public_url(file_name)
        print(f"URL generada: {public_url}")  # Para debugging
        return {
            "success": True,
            "path": public_url
        }
    except Exception as e:
        print(f"Error detallado al subir imagen: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def obtener_stock_total_juego(juego_id):
    """Obtiene el stock total de un juego específico por su ID."""
    total = Stock.objects.filter(juego_id=juego_id).aggregate(Sum('cantidad'))['cantidad__sum']
    return total or 0
