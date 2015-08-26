#!/usr/bin/env python

import unittest
import pandas as pd
from clima import parse_page

codes = ['SBGL', 'SBRJ','SBAF', 'SBJR']

class TestParse(unittest.TestCase):

    def test_can_parse(self):
        y=2015
        m=1
        d=3
        for code in codes:
            url = "http://www.wunderground.com/history/airport/{}/{}/{}/{}/DailyHistory.html??format=1&format=1".format(code,y,m,d)
            df = parse_page(url)
            self.assertIsInstance(df, pd.DataFrame)

    def test_can_convert_temperatures(self):
        def test_can_parse(self):
            y=2015
            m=1
            d=3
            for code in codes:
                url = "http://www.wunderground.com/history/airport/{}/{}/{}/{}/DailyHistory.html??format=1&format=1".format(code,y,m,d)
                df = parse_page(url)
                print df
                assert "TemperatureC" in df.columns




if __name__ == "__main__":
    unittest.main()