import unittest
import pymongo
from crawlclima.tasks import *
from crawlclima.fetchapp import app


mongo = pymongo.MongoClient()


app.conf.update(CELERY_ALWAYS_EAGER=True)

class TestTasks(unittest.TestCase):
    def test_pega_por_uf_escreve_no_Mongo(self):
        res = pega_dados_cemaden('RJ', '201505010000')
        col = mongo.clima.cemaden
        self.assertEquals(res, 200)

    def test_pega_tweets(self):
        res = pega_tweets("2015-05-01", "2015-05-07", [330455])
        self.assertEquals(res, 200)