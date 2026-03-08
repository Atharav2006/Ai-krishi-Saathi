import psycopg2

def try_pws():
    pws = ["password", "postgres", "admin", "admin123", "123456", "root"]
    for pw in pws:
        try:
            conn = psycopg2.connect(host="127.0.0.1", user="postgres", password=pw, dbname="postgres")
            print(f"SUCCESS|{pw}")
            conn.close()
            return
        except:
            pass
    print("ALL_FAILED")

if __name__ == "__main__":
    try_pws()
