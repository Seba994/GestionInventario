# diagnose_connection.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    print("🔍 Probando conexión a Supabase...")
    print(f"HOST: {os.getenv('HOST')}")
    print(f"USER: {os.getenv('USER')}")
    print(f"PORT: {os.getenv('PORT')}")
    print(f"DB NAME: {os.getenv('NAME')}")
    
    try:
        # Intenta con el pooler
        connection = psycopg2.connect(
            dbname=os.getenv('NAME'),
            user=os.getenv('USER'),
            password=os.getenv('PASSWORD'),
            host=os.getenv('HOST'),
            port=os.getenv('PORT'),
            sslmode="require"
        )
        print("✅ Conexión exitosa usando POOLER")
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error con pooler: {e}")
        
        try:
            # Intenta con conexión directa
            connection = psycopg2.connect(
                dbname=os.getenv('NAME'),
                user=os.getenv('USER'),
                password=os.getenv('PASSWORD'),
                host="db.scxjgurqofvbmoqlymwu.supabase.co",
                port="5432",
                sslmode="require"
            )
            print("✅ Conexión exitosa usando CONEXIÓN DIRECTA")
            connection.close()
            return True
            
        except Exception as e2:
            print(f"❌ Error con conexión directa: {e2}")
            return False

if __name__ == "__main__":
    test_connection()