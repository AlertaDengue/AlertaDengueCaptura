import psycopg2
from decouple import config


db_config = {
    'database': config('POSTGRES_DATABASE'),
    'user': config('POSTGRES_USER'),
    'password': config('POSTGRES_PASSWORD'),
    'host': config('POSTGRES_HOST'),
    'port': config('POSTGRES_PORT'),
}

field_names = {
    "Municipio": {
        'geocodigo': 'county_code',
        'nome': 'name',
        'geojson': 'geojson',
        'populacao': 'population',
        'uf': 'uf',
    },
    "Localidade": {
        '"Municipio_geocodigo"': 'county_code',
        'nome': 'name',
        'geojson': 'geojson',
        'populacao': 'population'
    },
    "Estacao_wu": {
        'estacao_id': 'ICAO',
        'nome': 'Estação',
        'latitude': 'Latitude',
        'longitude': 'Longitude',
    },
    "Clima_wu": {
        '"Estacao_wu_estacao_id"': 'station',
        'data_dia': 'date',
        'pressao_max': 'pressure_max',
        'pressao_med': 'pressure_mean',
        'pressao_min': 'pressure_min',
        'temp_max': 'temperature_max',
        'temp_med': 'temperature_mean',
        'temp_min': 'temperature_min',
        'umid_max': 'humidity_max',
        'umid_med': 'humidity_mean',
        'umid_min': 'humidity_min',
    },
}

join = lambda x: ', '.join(x)

def names_converter(field_names):
    def convert_names(datum):
        return {k: datum.get(v) for k, v in field_names.items()}
    return convert_names

def find_all(schema, table):
    table_full_name = '"{}"."{}"'.format(schema, table)
    sql_pattern = 'SELECT {} FROM {}'
    fields = field_names[table].keys()

    sql = sql_pattern.format(join(fields), table_full_name)

    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as curr:
            curr.execute(sql)
            rows = [dict(zip(fields, row)) for row in curr.fetchall()]

    conn.close() # Context doesn't close connection
    return rows

def save(data, schema='Dengue_global', table='Municipio'):
    table_full_name = '"{}"."{}"'.format(schema, table)
    sql_pattern = 'INSERT INTO {} ({}) VALUES ({})'

    fields = field_names[table].keys()
    binds = map(lambda k: '%({})s'.format(k), fields)

    sql = sql_pattern.format(table_full_name, join(fields), join(binds))

    convert_names = names_converter(field_names[table])

    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as curr:
            rows = map(convert_names, data)
            curr.executemany(sql, rows)

    conn.close() # Context doesn't close connection

