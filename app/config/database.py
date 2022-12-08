import psycopg2
from psycopg2.extras import RealDictCursor
import time

class Database:
    def __init__(self) -> None:
        self.conn = self.connect()

    def connect(self):

        cursor = None
        conn = None

        while True:
            try:
                conn = psycopg2.connect(host='localhost', database='investments', user='postgres', password='password',
                cursor_factory=RealDictCursor)
                cursor = conn.cursor()
                print("Database connection was succesfull!")

                cursor.execute("""
                                CREATE TABLE IF NOT EXISTS public.users (
                                id serial4 NOT NULL,
                                "name" varchar NOT NULL,
                                email varchar NOT NULL,
                                "password" varchar NOT NULL,
                                created_at timestamptz NOT NULL DEFAULT now(),
                                CONSTRAINT users_email_key UNIQUE (email),
                                CONSTRAINT users_pkey PRIMARY KEY (id)
                                );
                                """)

                cursor.execute("""
                                CREATE TABLE IF NOT EXISTS public.investments (
                                id serial4 NOT NULL,
                                investment_name varchar NOT NULL,
                                "token" varchar NULL,
                                amount float4 NOT NULL,
                                opening_at timestamptz NOT NULL DEFAULT now(),
                                CONSTRAINT investments_pkey PRIMARY KEY (id)
                                );
                            """)

                break
            except Exception as error:
                print("Connecting to Dabase failed")
                print(f"The error was: {error}")
                time.sleep(2)

        return conn, cursor