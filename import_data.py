import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("mysql_password"),
)

cursor = cnx.cursor()

# Create database
cursor.execute("CREATE DATABASE IF NOT EXISTS food_db")
cursor.execute("USE food_db")

# Read and execute SQL file
with open("food_database_dump.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()

for statement in sql_script.split(";"):
    if statement.strip():
        cursor.execute(statement)

# Verify database exists
cursor.execute("SHOW DATABASES LIKE 'food_db'")
print("DB:", cursor.fetchone())

# Verify tables were created
cursor.execute("SHOW TABLES")
print("Tables:", cursor.fetchall())

# Optional: check row count on a table
cursor.execute("SELECT COUNT(*) FROM comida")
print("Rows:", cursor.fetchone())

cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

for (table_name,) in tables:
    print("\nTABLE:", table_name)
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
    rows = cursor.fetchall()
    print(rows)

cnx.commit()
cursor.close()
cnx.close()