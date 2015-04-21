import unittest
import pymongo
from crawlclima.tasks import *
from crawlclima.fetchapp import app


mongo = pymongo.MongoClient()


app.conf.update(CELERY_ALWAYS_EAGER=True)

class TestTasks(unittest.TestCase):
    def test_pega_por_uf_escreve_no_Mongo(self):
        pega_dados_cemaden('RJ', '201501010000')
        col = mongo.clima.cemaden
        self.assertGreater(col.count(), 0)