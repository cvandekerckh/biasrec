from flask import Flask, render_template, request, make_response
import S2_star_lib as starz
import pandas as pd
import sqlite3
import csv
DBFILE = "stars.db"

# Read sqlite query results into a pandas DataFrame
con = sqlite3.connect(DBFILE)
df = pd.read_sql_query("SELECT * FROM `star_rating`", con)

# Verify that result of SQL query is stored in the dataframe
print(df)

#Conversion de la variable pandas en un fichier csv qui collecte tous les ratings 
d = pd.DataFrame(df)
d.to_csv('yourfile.csv', index=False)


con.close()

