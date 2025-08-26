# check_supabase_url.py
import os
from dotenv import load_dotenv

load_dotenv()

def check_supabase_url():
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    print("🔍 Verificando variables de Supabase:")
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SUPABASE_KEY: {supabase_key}")
    
    if not supabase_url:
        print("❌ SUPABASE_URL no está definida")
        return False
        
    if not supabase_key:
        print("❌ SUPABASE_KEY no está definida")
        return False
    
    # Verificar formato de URL
    if not supabase_url.startswith('https://'):
        print("❌ La URL debe comenzar con https://")
        return False
        
    if '.supabase.co' not in supabase_url:
        print("❌ La URL debe contener '.supabase.co'")
        return False
        
    print("✅ Formato de URL correcto")
    return True

if __name__ == "__main__":
    check_supabase_url()