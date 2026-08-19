""" Postgress DB connection """
from config import config_data
import psycopg2
from psycopg2 import DatabaseError
from psycopg2.extras import RealDictCursor

class PostgressDBConnect:
    @classmethod
    def get_db_connection(cls):
        cnf = config_data()

        try:
            conn = psycopg2.connect(
                host=cnf.DATABASE_URL,
                port=cnf.DB_PORT,
                database=cnf.DB_NAME,
                user=cnf.DB_USER,
                password=cnf.DB_PASS,
                cursor_factory=RealDictCursor
            )
            return conn
        except DatabaseError as error:
           raise RuntimeError(
                f"Database connection failure: {error}"
            ) from error
            

if __name__=='__main__':
    db_conn = PostgressDBConnect.get_db_connection()
    print(db_conn)
    if db_conn:
        db_conn.close()