import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection(): #get the connection to pgadmin postgres
    conn = psycopg2.connect(
        host = os.getenv("DB_HOST"),
        dbname = os.getenv("DB_NAME"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        port = os.getenv("DB_PORT")
    )
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS resumes(
                    id SERIAL PRIMARY KEY,
                    filename TEXT,
                    file_data BYTEA,
                    extracted_json JSONB,
                    ats_report JSONB,
                    enhanced_json JSONB
                );
              """  )
    conn.commit()
    cur.close()
    conn.close()
    print("Successfully Initialized the dataabse")
    
    
if __name__ == "__main__":
        init_db()
    