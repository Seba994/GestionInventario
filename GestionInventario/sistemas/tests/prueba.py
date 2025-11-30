from supabase import create_client

url = "https://vnhcanyqovgvolndtewv.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZuaGNhbnlxb3Zndm9sbmR0ZXd2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyODcxMzIsImV4cCI6MjA3Nzg2MzEzMn0.2953BYHPUtpP_GdYpZg73TrRKHa6cgX7EIMh6BxSJ2w"

client = create_client(url, key)

try:
    buckets = client.storage.list_buckets()
    print("BUCKETS =", buckets)
except Exception as e:
    print("ERROR =", e) 
    
