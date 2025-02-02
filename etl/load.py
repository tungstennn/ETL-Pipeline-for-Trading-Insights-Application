import psycopg2
import pandas as pd
from io import StringIO
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# PostgreSQL Connection Function
def connect_to_db():
    return psycopg2.connect(
        dbname=os.getenv("DB_name"),
        user=os.getenv("DB_username"),
        password=os.getenv("DB_password"),
        host=os.getenv("DB_host"),
        port=os.getenv("DB_port")
    )


# Function to Save Data to PostgreSQL
def save_to_db(df, table_name="market_data"):
    conn = connect_to_db()
    cur = conn.cursor()

    # Check if table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = %s
        );
    """, (table_name,))
    table_exists = cur.fetchone()[0]

    if not table_exists:
        # Create the table if it doesn't exist
        create_table_query = f"""
        CREATE TABLE student.{table_name} (
            datetime TIMESTAMP,
            open NUMERIC,
            high NUMERIC,
            low NUMERIC,
            close NUMERIC,
            volume NUMERIC,
            symbol VARCHAR(10),
            PRIMARY KEY (datetime, symbol)
        );
        """
        cur.execute(create_table_query)
        conn.commit()

    # Check for existing data (to handle deltas)
    cur.execute(f"SELECT datetime, symbol FROM student.{table_name}")
    existing_data = cur.fetchall()
    existing_set = set(existing_data)

    # Filter only new (delta) data
    df['datetime'] = pd.to_datetime(df['datetime'])
    delta_df = df[~df.set_index(['datetime', 'symbol']).index.isin(existing_set)]

    if not delta_df.empty:
        # Use COPY for efficient bulk insert
        buffer = StringIO()
        delta_df.to_csv(buffer, index=False, header=False)
        buffer.seek(0)

        copy_query = f"""
        COPY student.{table_name} (datetime, open, high, low, close, volume, symbol)
        FROM STDIN WITH (FORMAT CSV)
        """
        cur.copy_expert(copy_query, buffer)
        conn.commit()
        print(f"{len(delta_df)} new rows inserted into {table_name}.")
    else:
        print("No new data to insert.")

    cur.close()
    conn.close()
