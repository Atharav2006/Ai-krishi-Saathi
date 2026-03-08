import psycopg2

def test_psycopg2():
    combos = [
        {"user": "postgres", "password": "password", "dbname": "krishi_db"},
        {"user": "postgres", "password": "password", "dbname": "postgres"},
        {"user": "postgres", "password": "postgres", "dbname": "postgres"},
        {"user": "user", "password": "password", "dbname": "krishi_db"},
        {"user": "postgres", "password": "", "dbname": "postgres"}, # No password
    ]
    
    for c in combos:
        print(f"Testing {c}...")
        try:
            conn = psycopg2.connect(
                host="127.0.0.1",
                port=5432,
                user=c['user'],
                password=c['password'],
                dbname=c['dbname'],
                connect_timeout=3
            )
            print(f"SUCCESS: {c}")
            conn.close()
            return c
        except Exception as e:
            print(f"FAILED: {e}")
    return None

if __name__ == "__main__":
    test_psycopg2()
