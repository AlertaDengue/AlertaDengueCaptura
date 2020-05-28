#
import os

from dotenv import load_dotenv

load_dotenv()

psql_host = os.getenv("PSQL_HOST")
psql_user = os.getenv("PSQL_USER")
