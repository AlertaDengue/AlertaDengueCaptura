#!/usr/bin/env python

from datetime import datetime
import unittest
import pandas as pd
from crawlclima.redemet.rmet import (parse_page, fahrenheit_to_celsius,
                                     wu_url, date_generator, describe,
                                     capture_date_range, capture)


class TestFahrenheitToCelsius(unittest.TestCase):
    def test_32(self):
        self.assertEqual(fahrenheit_to_celsius(32), 0)

    def test_212(self):
        self.assertEqual(fahrenheit_to_celsius(212), 100)

    def test_0(self):
        self.assertAlmostEqual(fahrenheit_to_celsius(0), -17.78, 2)


class TestCapture(unittest.TestCase):
    def test_capture_return_type(self):
        station_code = 'SBAF'
        date = datetime(2015, 11, 2)
        data = capture(station_code, date)
        self.assertIsInstance(data, dict)

    def test_capture_range(self):
        station_code = 'SBAF'
        date = datetime(2015, 11, 2)
        data = capture_date_range(station_code, date)
        self.assertIsInstance(data, list)

    def test_check_day(self):
        pass


class TestWUUrl(unittest.TestCase):
    def test_SBGL_20150228(self):
        station_code = 'SBGL'
        date = datetime(2015, 2, 28)
        url = "http://www.wunderground.com/history/airport/SBGL/2015/2/28/DailyHistory.html?format=1"

        self.assertEqual(wu_url(station_code, date), url)

    def test_SBJR_20150131(self):
        station_code = 'SBJR'
        date = datetime(2015, 1, 31)
        url = "http://www.wunderground.com/history/airport/SBJR/2015/1/31/DailyHistory.html?format=1"

        self.assertEqual(wu_url(station_code, date), url)


class TestDateGenerator(unittest.TestCase):
    def test_one_url(self):
        start = datetime(2015, 2, 28)
        dates = [
            datetime(2015, 2, 28),
        ]

        generated_dates = list(date_generator(start))
        self.assertEqual(generated_dates, dates)

    def test_crossing_months(self):
        start = datetime(2015, 1, 30)
        end = datetime(2015, 2, 3)
        dates = [
            datetime(2015, 1, 30),
            datetime(2015, 1, 31),
            datetime(2015, 2, 1),
            datetime(2015, 2, 2),
        ]

        generated_dates = list(date_generator(start, end))
        self.assertEqual(generated_dates, dates)

    def test_crossing_years(self):
        start = datetime(2015, 12, 31)
        end = datetime(2016, 1, 2)
        dates = [
            datetime(2015, 12, 31),
            datetime(2016, 1, 1),
        ]

        generated_dates = list(date_generator(start, end))
        self.assertEqual(generated_dates, dates)

    def test_starting_from_a_bigger_date(self):
        start = datetime(2015, 12, 31)
        end = datetime(2015, 12, 28)
        dates = [
            datetime(2015, 12, 31),
            datetime(2015, 12, 30),
            datetime(2015, 12, 29),
        ]

        generated_dates = list(date_generator(start, end))
        self.assertEqual(generated_dates, dates)


class TestParsePage(unittest.TestCase):
    def testCelsiusDailyHistory(self):
        with open('crawlclima/redemet/tests/CelsiusDailyHistory.html', 'r') as fd:
            dataframe = parse_page(fd.read())
        self.assertEqual(dataframe.DateUTC[0], '2015-08-01 03:00:00')
        self.assertAlmostEqual(dataframe.TemperatureC.mean(), 24.33, 2)

    def testEmptyDailyHistory(self):
        with open('crawlclima/redemet/tests/EmptyDailyHistory.html', 'r') as fd:
            dataframe = parse_page(fd.read())

        self.assertIsInstance(dataframe, pd.DataFrame)
        self.assertTrue(dataframe.empty)

    @unittest.skip("Test a case with no Celsius temp")
    def testFahrenheitDailyHistory(self):
        pass


class TestDescribe(unittest.TestCase):
    def test_filled_dataframe(self):
        with open('crawlclima/redemet/tests/CelsiusDailyHistory.html', 'r') as fd:
            dataframe = parse_page(fd.read())

        summary = describe(dataframe)
        self.assertEqual(summary, {
            'humidity_max': 100.0,
            'humidity_mean': 79.799999999999997,
            'humidity_min': 47.0,
            'pressure_max': 1021.0,
            'pressure_mean': 1019.0689655172414,
            'pressure_min': 1017.0,
            'temperature_max': 33.0,
            'temperature_mean': 24.333333333333332,
            'temperature_min': 21.0
        })

    def test_empty_dataframe(self):
        with open('crawlclima/redemet/tests/EmptyDailyHistory.html', 'r') as fd:
            dataframe = parse_page(fd.read())

        summary = describe(dataframe)
        self.assertEqual(summary, {})


if __name__ == "__main__":
    unittest.main()
