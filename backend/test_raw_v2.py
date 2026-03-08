import psycopg2

def test_psycopg2():
    combos = [
        ("krishi_db", "user", "password"),
        ("krishi_db", "postgres", "password"),
        ("postgres", "postgres", "password"),
        ("postgres", "postgres", "postgres"),
        ("krishi_db", "postgres", "postgres"),
    ]
    
    for db, user, pw in combos:
        try:
            conn = psycopg2.connect(
                host="127.0.0.1",
                port=5432,
                user=user,
                password=pw,
                dbname=db,
                connect_timeout=2
            )
            print(f"|SUCCESS|DB={db}|USER={user}|PW={pw}|")
            conn.close()
            return
        except Exception as e:
            msg = str(e).strip().replace('\n', ' ')
            print(f"|FAIL|DB={db}|USER={user}|PW={pw}|ERR={msg}|")

if __name__ == "__main__":
    test_psycopg2()
