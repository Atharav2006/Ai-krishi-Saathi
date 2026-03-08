import psycopg2

def test_ipv6():
    try:
        conn = psycopg2.connect(
            host="::1",
            port=5432,
            user="postgres",
            password="password",
            dbname="postgres",
            connect_timeout=2
        )
        print("CONNECTED via IPv6")
        conn.close()
    except Exception as e:
        print(f"FAILED IPv6: {e}")

if __name__ == "__main__":
    test_ipv6()
