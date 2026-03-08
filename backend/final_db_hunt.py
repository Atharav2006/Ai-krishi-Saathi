import psycopg2
import os

def final_test():
    # Try common local dev passwords or trust
    attempts = [
        {"user": "postgres", "password": "", "host": "127.0.0.1"},
        {"user": "postgres", "password": "password", "host": "127.0.0.1"},
        {"user": "postgres", "password": "postgres", "host": "127.0.0.1"},
        {"user": "postgres", "password": "", "host": "localhost"},
    ]
    
    for a in attempts:
        try:
            conn = psycopg2.connect(
                host=a["host"],
                user=a["user"],
                password=a["password"],
                dbname="postgres",
                connect_timeout=2
            )
            print(f"CONNECTED: {a}")
            cur = conn.cursor()
            cur.execute("SELECT datname FROM pg_database;")
            dbs = [r[0] for r in cur.fetchall()]
            print(f"Databases: {dbs}")
            conn.close()
            return a
        except Exception as e:
            print(f"FAILED {a}: {str(e).strip()}")
    return None

if __name__ == "__main__":
    final_test()
