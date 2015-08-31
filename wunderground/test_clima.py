#!/usr/bin/env python

import unittest
import pandas as pd
from clima import parse_page, fahrenheit_to_celsius

codes = ['SBGL', 'SBRJ','SBAF', 'SBJR']

class TestFahrenheitToCelsius(unittest.TestCase):
    def test_32(self):
        self.assertEqual(fahrenheit_to_celsius(32), 0)

    def test_212(self):
        self.assertEqual(fahrenheit_to_celsius(212), 100)

    def test_212(self):
        self.assertAlmostEqual(fahrenheit_to_celsius(0), -17.78, 2)

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
                print(df)
                assert "TemperatureC" in df.columns




if __name__ == "__main__":
    unittest.main()
