import unittest
import psycopg2
import sys
from crawlclima.tasks import *
from crawlclima.fetchapp import app

try:
    conn = psycopg2.connect("dbname='dengue' user='{}' host='{}' password='aldengue'".format('dengueadmin', '127.0.0.1'))
except Exception as e:
    logger.error("Unable to connect to Postgresql: {}".format(e))
    sys.exit()


app.conf.update(CELERY_ALWAYS_EAGER=True)

class TestTasks(unittest.TestCase):
    def setUp(self):
        self.cur = conn.cursor()

    def tearDown(self):
        self.cur.close()

    def test_pega_por_uf_escreve_no_banco(self):
        res = pega_dados_cemaden('RJ', '201508100000', '201508120000')
        self.cur.execute('select * from "Municipio"."Clima_cemaden";')
        resp = self.cur.fetchall()
        self.assertEquals(res, 200)
        self.assertGreaterEqual(len(resp), 0)

    def test_pega_tweets(self):
        res = pega_tweets("2015-01-01", "2015-08-07", ['3304557', '3303302'])
        self.cur.execute('select * from "Municipio"."Tweet";')
        resp = self.cur.fetchall()
        self.assertEquals(res, 200)
        self.assertGreater(len(resp), 0)

if __name__ == "__main__":
    pass
    # TestTasks().run()
