import os
import unittest

import pandas as pd
import psycopg2
from dotenv import load_dotenv

from utilities.load_sinan import Sinan, calculate_digit

load_dotenv()


db_config = {
    "database": os.getenv("POSTGRES_DATABASE"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
}


class TestSinan(unittest.TestCase):
    def setUp(self):
        self.S = Sinan("Dengue2014_23_03_2015.dbf", 2014)

    # @skip
    def test_load_dbf_into_dataframe(self):
        self.assertIsInstance(self.S.tabela, pd.DataFrame)

    # @skip
    def test_date_columns_are_datetime(self):
        for nome in filter(
            lambda x: x.startswith("DT"), self.S.colunas_entrada
        ):
            self.assertIsInstance(
                self.S.tabela[nome].iloc[0],
                (pd.Timestamp, pd.tslib.NaTType),
                "{}".format(nome),
            )

    # @skip
    def test_timespan_returns_times(self):
        td = self.S.time_span
        self.assertIsInstance(td[0], pd.Timestamp)
        self.assertIsInstance(td[1], pd.Timestamp)
        self.assertGreater(td[1], td[0])

    def test_save_to_postgresql(self):
        conn = psycopg2.connect(**db_config)
        self.S.save_to_pgsql(conn)
        cur = conn.cursor()
        cur.execute(
            'select count(*) from "Municipio"."Notificacao" where ano_notif=2014'
        )
        res = cur.fetchone()[0]
        cur.close()
        conn.close()
        self.assertEquals(len(self.S.tabela), res)

    def test_calculate_digit(self):
        dig_rio = calculate_digit(330455)
        dig_nit = calculate_digit(330330)
        dig3 = calculate_digit(170190)
        self.assertEqual(dig_rio, 7)
        self.assertEqual(dig_nit, 2)
        self.assertEqual(dig3, 3)
