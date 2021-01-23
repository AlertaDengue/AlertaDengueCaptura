"""
COnfiguration details for the capture of tweets
"""
import os

from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)


base_url = "http://observatorio.inweb.org.br/dengueapp/api/1.0/totais"
token = "XXXXX"

psql_host = os.getenv("PSQL_HOST")
psql_port = os.getenv("PSQL_PORT")
psql_user = os.getenv("PSQL_USER")
psql_db = os.getenv("PSQL_DB")
psql_password = os.getenv("PSQL_PASSWORD")
