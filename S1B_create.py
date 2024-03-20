#Lecture du fichier SQL et création de la base de données
# (A) LOAD PACKAGES
import sqlite3, os
from sqlite3 import Error

# (B) DATABASE + SQL FILE
DBFILE = "stars.db" 
SQLFILE = "S1A_database.sql"

# (C) DELETE OLD DATABASE IF EXIST
if os.path.exists(DBFILE):
  os.remove(DBFILE)

# (D) IMPORT SQL
conn = sqlite3.connect(DBFILE)
with open(SQLFILE) as f:
  conn.executescript(f.read())
conn.commit()
conn.close()
print("Database created!")