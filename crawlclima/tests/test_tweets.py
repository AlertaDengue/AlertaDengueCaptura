import csv
import unittest
from io import StringIO

import requests


class TestCapture(unittest.TestCase):
    def test_pega_tweets(self):
        url = 'https://observatorio.inweb.org.br/dengueapp/api/1.0/totais?'
        cities = ['355650', '355660', '355695']
        params = (
            'cidade='
            + '&cidade='.join(cities)
            + '&inicio='
            + '2021-10-12'
            + '&fim='
            + '2021-10-20'
            + '&token='
            + 'XXXXX'
        )

        response = requests.get(url, params=params)

        header = ['data'] + cities
        fp = StringIO(response.text)
        data = list(csv.DictReader(fp, fieldnames=header))

        expected_data = [
            {
                'data': 'data',
                '355650': '355650',
                '355660': '355660',
                '355695': '355695',
            },
            {
                'data': '2021-10-14',
                '355650': '0',
                '355660': '0',
                '355695': '1',
            },
            {
                'data': '2021-10-15',
                '355650': '0',
                '355660': '0',
                '355695': '2',
            },
            {
                'data': '2021-10-16',
                '355650': '0',
                '355660': '0',
                '355695': '1',
            },
            {
                'data': '2021-10-17',
                '355650': '0',
                '355660': '0',
                '355695': '1',
            },
            {
                'data': '2021-10-18',
                '355650': '1',
                '355660': '0',
                '355695': '0',
            },
        ]

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.headers['Content-Type'], 'text/html; charset=utf-8'
        )
        self.assertEqual(expected_data, data)


if __name__ == '__main__':
    pass
    TestCapture().test_pega_tweets()
