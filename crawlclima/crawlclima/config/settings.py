import os

from dotenv import load_dotenv

local = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
dotenv_path = os.path.join(local, '.env')
load_dotenv(dotenv_path)


base_url = 'http://observatorio.inweb.org.br/dengueapp/api/1.0/totais'
token = 'XXXXX'

db_config = {
    'database': os.getenv('PSQL_DB'),
    'user': os.getenv('PSQL_USER'),
    'password': os.getenv('PSQL_PASSWORD'),
    'host': os.getenv('PSQL_HOST'),
    'port': os.getenv('PSQL_PORT'),
}
