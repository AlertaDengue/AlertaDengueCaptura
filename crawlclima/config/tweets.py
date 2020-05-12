"""
COnfiguration details for the capture of tweets
"""
from decouple import config

base_url = "http://observatorio.inweb.org.br/dengueapp/api/1.0/totais"
token = "XXXXX"

psql_host = config("POSTGRES_HOST")
psql_port = config("POSTGRES_PORT")
psql_user = config("POSTGRES_USER")
psql_db = config("POSTGRES_DATABASE")
psql_password = config("POSTGRES_PASSWORD")
