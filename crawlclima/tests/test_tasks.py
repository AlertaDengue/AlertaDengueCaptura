import logging
import os
import sys
import unittest
from datetime import timedelta

import psycopg2
from dotenv import load_dotenv

from crawlclima.fetchapp import app
from crawlclima.tasks import pega_dados_cemaden, pega_tweets

load_dotenv()


logger = logging.getLogger(__name__)  # Verify where this logger comes from

try:
    conn = psycopg2.connect(
        "dbname='{}' user='{}' host='{}' password='{}'".format(
            os.getenv("POSTGRES_DATABASE"),
            os.getenv("POSTGRES_USER"),
            os.getenv("POSTGRES_HOST"),
            os.getenv("POSTGRES_PASSWORD"),
        )
    )
except Exception as e:
    logger.error("Unable to connect to Postgresql: {}".format(e))
    sys.exit()


app.conf.update(CELERY_ALWAYS_EAGER=True)


@unittest.skip("reason='Enable base_demo for testing'")
class TestTasks(unittest.TestCase):
    def setUp(self):
        self.cur = conn.cursor()

    def tearDown(self):
        self.cur.close()

    def test_pega_novos_dados_cemaden(self):
        self.cur.execute(
            'select datahora from "Municipio"."Clima_cemaden" order by datahora DESC ;'
        )
        lastdate = self.cur.fetchone()[0]
        res = pega_dados_cemaden("RJ", lastdate, lastdate + timedelta(1))
        self.cur.execute('select * from "Municipio"."Clima_cemaden";')
        resp = self.cur.fetchall()
        self.assertEquals(res, 200)
        self.assertGreaterEqual(len(resp), 0)

    def test_tries_to_fetch_data_which_is_already_in_DB(self):
        res = pega_dados_cemaden("RJ", "201508100000", "201508120000")
        self.cur.execute('select * from "Municipio"."Clima_cemaden";')
        resp = self.cur.fetchall()
        self.assertEquals(res, None)
        self.assertGreaterEqual(len(resp), 0)

    def test_pega_tweets(self):
        res = pega_tweets("2015-01-01", "2015-08-07", ["3304557", "3303302"])
        self.cur.execute('select * from "Municipio"."Tweet";')
        resp = self.cur.fetchall()
        self.assertEqual(res, 200)
        self.assertGreater(len(resp), 0)


if __name__ == "__main__":
    pass
    # TestTasks().run()
