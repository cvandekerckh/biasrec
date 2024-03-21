from flask import Flask, render_template, request, make_response
import pandas as pd
import sqlite3
import csv
DBFILE = "stars.db"

# Read sqlite query results into a pandas DataFrame
con = sqlite3.connect(DBFILE)
df = pd.read_sql_query("SELECT * FROM `star_rating`", con)

# Verify that result of SQL query is stored in the dataframe
print(df)

con.close()

