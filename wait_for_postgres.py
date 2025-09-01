
import os, time, sys
import psycopg

url = os.getenv("DATABASE_URL", "postgresql+psycopg://botuser:botpass@db:5432/botdb")
plain = url.replace("+psycopg", "").replace("+psycopg2", "")

for _ in range(60):
    try:
        with psycopg.connect(plain, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                print("[wait] PostgreSQL is ready.")
                sys.exit(0)
    except Exception as e:
        print("[wait] waiting for PostgreSQL...", str(e))
        time.sleep(2)

print("[wait] PostgreSQL did not become ready in time.")
sys.exit(1)
