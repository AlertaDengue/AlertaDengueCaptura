#!/usr/bin/env python
import os
import re
import unittest
from datetime import datetime, timedelta
from unittest import mock

import pandas as pd
import responses
from dotenv import load_dotenv

from crawlclima.redemet.rmet import (
    capture,
    capture_date_range,
    clean_line,
    date_generator,
    describe,
    fahrenheit_to_celsius,
    get_date_and_standard_metar,
    humidity,
    parse_page,
    redemet_url,
)

load_dotenv()


class TestFahrenheitToCelsius(unittest.TestCase):
    def test_32(self):
        self.assertEqual(fahrenheit_to_celsius(32), 0)

    def test_212(self):
        self.assertEqual(fahrenheit_to_celsius(212), 100)

    def test_0(self):
        self.assertAlmostEqual(fahrenheit_to_celsius(0), -17.78, 2)


class TestCapture(unittest.TestCase):
    @responses.activate
    @mock.patch("crawlclima.redemet.rmet.time.sleep")
    def test_capture_return_type(self, mocked_sleep):
        with open(
            "crawlclima/redemet/tests/test_example_data.json", "r"
        ) as fd:
            response_text = fd.read()

        api_key = os.getenv("API_KEY")
        station_code = "SBAF"
        date = datetime(2020, 6, 25)

        responses.add(
            responses.GET,
            "https://api-redemet.decea.gov.br/mensagens/metar/{}?"
            "api_key={}"
            "&data_ini=2020062500&data_fim=2020062523".format(
                station_code, api_key
            ),
            body=response_text,
        )

        data = capture(station_code, date)
        self.assertIsInstance(data, dict)

    @responses.activate
    @mock.patch("crawlclima.redemet.rmet.time.sleep")
    def test_capture_range(self, mocked_sleep):
        with open(
            "crawlclima/redemet/tests/test_example_data.json", "r"
        ) as fd:
            response_text = fd.read()

        station_code = "SBSR"
        date = datetime.today() - timedelta(3)

        url_pattern = re.compile(
            r'https://api-redemet\.decea\.gov\.br/mensagens/metar/'
            r'SBSR\?api_key=.*data_ini=.*data_fim=.*'
        )

        responses.add(
            method=responses.GET, url=url_pattern, body=response_text
        )

        data = capture_date_range(station_code, date)
        self.assertIsInstance(data, list)
        self.assertEqual(len(responses.calls), 2)

    def test_check_day(self):
        pass


class TestREDEMETUrl(unittest.TestCase):
    def test_SBGL_20200625(self):
        api_key = os.getenv("API_KEY")
        station_code = "SBGL"
        date = datetime(2020, 6, 25)
        formatted_ini = date.strftime("%Y%m%d")
        formatted_fim = date.strftime("%Y%m%d")

        url = (
            "https://api-redemet.decea.gov.br/mensagens/metar/{}?"
            "api_key={}"
            "&data_ini={}00&data_fim={}23".format(
                station_code, api_key, formatted_ini, formatted_fim
            )
        )

        self.assertEqual(redemet_url(station_code, date), url)

    def test_SBJR_20200625(self):
        api_key = os.getenv("API_KEY")
        station_code = "SBRJ"
        date = datetime(2020, 6, 25)
        formatted_ini = date.strftime("%Y%m%d")
        formatted_fim = date.strftime("%Y%m%d")

        url = (
            "https://api-redemet.decea.gov.br/mensagens/metar/{}?"
            "api_key={}"
            "&data_ini={}00&data_fim={}23".format(
                station_code, api_key, formatted_ini, formatted_fim
            )
        )

        self.assertEqual(redemet_url(station_code, date), url)


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


class TestGetDateAndStandardMetarFromRedemet(unittest.TestCase):
    def test_remove_non_standard_fields(self):
        raw_data = (
            "2015022819 - METAR SBGL 281900Z 16013KT"
            " 9999 SCT025 FEW030TCU 29/22 Q1012="
        )
        expected_standard_data = (
            "METAR SBGL 281900Z 16013KT" " 9999 SCT025 FEW030TCU 29/22 Q1012"
        )
        observation_time, standard_data = get_date_and_standard_metar(raw_data)
        self.assertEqual(standard_data, expected_standard_data)

    def test_observation_time_is_extracted_from_non_standard_field(self):
        raw_data = (
            "2015022819 - METAR SBGL 281900Z 16013KT"
            " 9999 SCT025 FEW030TCU 29/22 Q1012="
        )
        expected_observation_time = datetime(2015, 2, 28, 19, 0)
        observation_time, standard_data = get_date_and_standard_metar(raw_data)
        self.assertEqual(observation_time, expected_observation_time)

    def test_remove_COR_modifier(self):
        """
        This modifier is not important for us, but it breaks Metar because
        REDEMET sends it in a non-standard position (Metar expects is
        after the sation, but it comes before).
        """
        raw_data = (
            "2017111718 - METAR COR SBAT 171800Z 28004KT "
            "9999 SCT035 FEW040TCU 33/24 Q1008="
        )
        expected_observation_time = datetime(2017, 11, 17, 18, 0)
        observation_time, standard_data = get_date_and_standard_metar(raw_data)
        self.assertEqual(observation_time, expected_observation_time)
        self.assertNotIn("COR", standard_data)


class TestCleanLine(unittest.TestCase):

    regular_entry = (
        "2015022800 - METAR SBGL 280000Z " "14006KT CAVOK 27/22 Q1009="
    )

    def test_remove_SPECI_entries(self):
        speci_entry = (
            "2015022821 - SPECI SBGL 282120Z 14013KT"
            " 4000 -RA FEW009 SCT020 FEW030TCU BKN040"
            " 25/23 Q1013="
        )
        lines = [self.regular_entry, speci_entry, self.regular_entry]
        result = filter(clean_line, lines)
        self.assertEqual(
            list(result), [self.regular_entry, self.regular_entry]
        )

    def test_remove_empty_lines(self):
        lines = [self.regular_entry, "", self.regular_entry]
        result = filter(clean_line, lines)
        self.assertEqual(
            list(result), [self.regular_entry, self.regular_entry]
        )

    def test_remove_lines_with_no_pressure_information(self):
        no_pressure_entry = (
            "2017120417 - METAR SBAT 041700Z 16003KT 9999 "
            "VCSH FEW030 FEW035TCU BKN100 33/25 Q////="
        )
        lines = [self.regular_entry, no_pressure_entry, self.regular_entry]
        result = filter(clean_line, lines)
        self.assertEqual(
            list(result), [self.regular_entry, self.regular_entry]
        )

    def test_remove_lines_with_information_missing(self):
        """
        REDEMET can send entries with missing information. In this cases,
        '////' is used as a placeholder. We should ignore this lines.
        """
        missing_info_entry = (
            "METAR SBAN 061000Z 33005KT 0500 R24R///// "
            "R06L/0450 FG OVC004 18/17 Q1020="
        )
        lines = [self.regular_entry, missing_info_entry, self.regular_entry]
        result = filter(clean_line, lines)
        self.assertEqual(
            list(result), [self.regular_entry, self.regular_entry]
        )

    def test_remove_too_long_entries(self):
        """
        python-metar can't parse this example (seen in REDEMET on
        2017-11-16 at 10:00). It looks like REDEMET is sending too many
        cloud information fields.
        """
        long_entry = (
            "METAR SBAT 161000Z 1612/1624 09005KT 9999 SCT015 "
            "TN26/1612Z TX32/1618Z BECMG 1615/1617 06005KT "
            "SCT030 FEW035TCU PROB30 1619/1621 TS SCT020 "
            "FEW025CB BECMG 1621/1623 00000KT FEW020 RMK PEH="
        )
        lines = [self.regular_entry, long_entry, self.regular_entry]
        result = filter(clean_line, lines)
        self.assertEqual(
            list(result), [self.regular_entry, self.regular_entry]
        )

    def test_remove_lines_when_there_is_no_data(self):
        no_data_msg = (
            "Mensagem de 'SBGL' para 28/02/2018"
            " as 00(UTC) não localizada na base"
            " de dados da REDEMET"
        )
        lines = [self.regular_entry, no_data_msg, self.regular_entry]
        result = filter(clean_line, lines)
        self.assertEqual(
            list(result), [self.regular_entry, self.regular_entry]
        )


class TestCalculateHumidity(unittest.TestCase):
    def test_calculate_humidity(self):
        temperature = 25
        dew_point = 22
        self.assertAlmostEqual(humidity(temperature, dew_point), 83.45, 2)


class TestParsePage(unittest.TestCase):
    def test_skip_SPECI_entries(self):
        with open("crawlclima/redemet/tests/example_data.txt", "r") as fd:
            dataframe = parse_page(fd.read())
        self.assertEqual(len(dataframe), 24)

    def test_with_data(self):
        with open("crawlclima/redemet/tests/example_data.txt", "r") as fd:
            dataframe = parse_page(fd.read())
        self.assertEqual(
            dataframe.observation_time[0].to_pydatetime(),
            datetime(2015, 2, 28, 0, 0),
        )
        self.assertAlmostEqual(dataframe.temperature.mean(), 27.75, 2)

    def test_with_empty_data(self):
        with open(
            "crawlclima/redemet/tests/" "example_with_no_record.txt", "r"
        ) as fd:
            dataframe = parse_page(fd.read())

        self.assertIsInstance(dataframe, pd.DataFrame)
        self.assertTrue(dataframe.empty)

    def test_includes_humidity(self):
        with open("crawlclima/redemet/tests/example_data.txt", "r") as fd:
            dataframe = parse_page(fd.read())
        self.assertAlmostEqual(dataframe.humidity.min(), 55.32, 2)


class TestDescribe(unittest.TestCase):
    def test_filled_dataframe(self):
        with open("crawlclima/redemet/tests/example_data.txt", "r") as fd:
            dataframe = parse_page(fd.read())

        summary = describe(dataframe)
        self.assertEqual(
            summary,
            {
                "humidity_max": 88.679561374670186,
                "humidity_mean": 73.687275217443982,
                "humidity_min": 55.321861254558726,
                "pressure_max": 1014.0,
                "pressure_mean": 1010.9583333333334,
                "pressure_min": 1008.0,
                "temperature_max": 31.0,
                "temperature_mean": 27.75,
                "temperature_min": 25.0,
            },
        )

    def test_empty_dataframe(self):
        with open(
            "crawlclima/redemet/tests/" "example_with_no_record.txt", "r"
        ) as fd:
            dataframe = parse_page(fd.read())

        summary = describe(dataframe)
        self.assertEqual(summary, {})


if __name__ == "__main__":
    unittest.main()
