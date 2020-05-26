"""
COnfiguration details for the capture of tweets
"""
import os

from dotenv import load_dotenv


base_url = "http://observatorio.inweb.org.br/dengueapp/api/1.0/totais"
token = "XXXXX"

psql_host = os.getenv("POSTGRES_HOST")
psql_port = os.getenv("POSTGRES_PORT")
psql_user = os.getenv("POSTGRES_USER")
psql_db = os.getenv("POSTGRES_DATABASE")
psql_password = os.getenv("POSTGRES_PASSWORD")
print("Hi Sandro Tweets")
print(psql_host)