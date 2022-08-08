import psycopg2
import os

connection = psycopg2.connect(
    database=os.getenv('PG_PASSWORD'),
    password=os.getenv('PG_PASSWORD'),
    user=os.getenv('PG_USER'),
    host=os.getenv('PG_HOST'),
    port=os.getenv('PG_PORT')
)
connection.autocommit = True

user = """
CREATE TABLE IF NOT EXISTS user_tb(
id SERIAL 
)
"""

posts = """
CREATE TABLE IF NOT EXISTS news_table(
id SERIAL PRIMARY KEY, 
)
"""