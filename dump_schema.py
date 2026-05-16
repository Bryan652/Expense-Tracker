import os
import psycopg
from dotenv import load_dotenv

def dump_schema():
    load_dotenv(override=True)
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("DATABASE_URL not found in environment.")
        return

    try:
        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cur:
                # Get all public tables
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = [row[0] for row in cur.fetchall()]
                
                with open("schema_context.txt", "w") as f:
                    f.write("Database Schema (NeonDB)\n")
                    f.write("========================\n\n")
                    
                    for table in tables:
                        f.write(f"Table: {table}\n")
                        f.write("-" * 20 + "\n")
                        
                        # Get columns for the table
                        cur.execute(f"""
                            SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
                            FROM information_schema.columns 
                            WHERE table_schema = 'public' AND table_name = '{table}'
                            ORDER BY ordinal_position;
                        """)
                        columns = cur.fetchall()
                        
                        for col in columns:
                            col_name, data_type, max_len, is_null, default_val = col
                            type_str = f"{data_type}({max_len})" if max_len else data_type
                            null_str = "NULL" if is_null == "YES" else "NOT NULL"
                            default_str = f" DEFAULT {default_val}" if default_val else ""
                            f.write(f"  - {col_name}: {type_str} {null_str}{default_str}\n")
                        f.write("\n")
                        
        print("Successfully exported live database schema to schema_context.txt")
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    dump_schema()
