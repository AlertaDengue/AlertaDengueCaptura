#!/usr/bin/env python

from datetime import datetime
import unittest
import pandas as pd
from clima import parse_page, fahrenheit_to_celsius, wu_url_generator

codes = ['SBGL', 'SBRJ','SBAF', 'SBJR']

class TestFahrenheitToCelsius(unittest.TestCase):
    def test_32(self):
        self.assertEqual(fahrenheit_to_celsius(32), 0)

    def test_212(self):
        self.assertEqual(fahrenheit_to_celsius(212), 100)

    def test_212(self):
        self.assertAlmostEqual(fahrenheit_to_celsius(0), -17.78, 2)


class TestWUUrlGenerator(unittest.TestCase):
    def test_one_url(self):
        station_code = 'SBGL'
        start = datetime(2015, 2, 28)
        urls = [
            "http://www.wunderground.com/history/airport/SBGL/2015/2/28/DailyHistory.html?format=1",
            ]

        generated_urls = list(wu_url_generator(station_code, start))
        self.assertEqual(generated_urls, urls)

    def test_crossing_months(self):
        station_code = 'SBJR'
        start = datetime(2015, 1, 30)
        end = datetime(2015, 2, 3)
        urls = [
            "http://www.wunderground.com/history/airport/SBJR/2015/1/30/DailyHistory.html?format=1",
            "http://www.wunderground.com/history/airport/SBJR/2015/1/31/DailyHistory.html?format=1",
            "http://www.wunderground.com/history/airport/SBJR/2015/2/1/DailyHistory.html?format=1",
            "http://www.wunderground.com/history/airport/SBJR/2015/2/2/DailyHistory.html?format=1",
            ]

        generated_urls = list(wu_url_generator(station_code, start, end))
        self.assertEqual(generated_urls, urls)

    def test_crossing_years(self):
        station_code = 'SBAF'
        start = datetime(2015, 12, 31)
        end = datetime(2016, 1, 2)
        urls = [
            "http://www.wunderground.com/history/airport/SBAF/2015/12/31/DailyHistory.html?format=1",
            "http://www.wunderground.com/history/airport/SBAF/2016/1/1/DailyHistory.html?format=1",
            ]

        generated_urls = list(wu_url_generator(station_code, start, end))
        self.assertEqual(generated_urls, urls)

    def test_stating_from_a_bigger_date(self):
        station_code = 'SBRJ'
        start = datetime(2015, 12, 31)
        end = datetime(2015, 12, 28)
        urls = [
            "http://www.wunderground.com/history/airport/SBRJ/2015/12/31/DailyHistory.html?format=1",
            "http://www.wunderground.com/history/airport/SBRJ/2015/12/30/DailyHistory.html?format=1",
            "http://www.wunderground.com/history/airport/SBRJ/2015/12/29/DailyHistory.html?format=1",
            ]

        generated_urls = list(wu_url_generator(station_code, start, end))
        self.assertEqual(len(generated_urls), 3)
        self.assertEqual(generated_urls, urls)


class TestParsePage(unittest.TestCase):
    def testCelsiusDailyHistory(self):
        with open('wunderground/CelsiusDailyHistory.html', 'r') as fd:
            dataframe = parse_page(fd.read())
        self.assertEqual(dataframe.DateUTC[0], '2015-08-01 03:00:00')
        self.assertAlmostEqual(dataframe.TemperatureC.mean(), 24.33, 2)

    def testEmptyDailyHistory(self):
        with open('wunderground/EmptyDailyHistory.html', 'r') as fd:
            dataframe = parse_page(fd.read())

        self.assertIsInstance(dataframe, pd.DataFrame)
        self.assertTrue(dataframe.empty)

    @unittest.skip("Test a case with no Celsius temp")
    def testFahrenheitDailyHistory(self):
        pass


if __name__ == "__main__":
    unittest.main()
