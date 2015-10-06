import psycopg2
from decouple import config


db_config = {
    'database': config('POSTGRES_DATABASE'),
    'user': config('POSTGRES_USER'),
    'password': config('POSTGRES_PASSWORD'),
    'host': config('POSTGRES_HOST'),
    'port': config('POSTGRES_PORT'),
}

field_names = {'"Municipio_geocodigo"': 'county_code',
                'id': 'county_code', # TODO: Validate this equivalence.
                'nome': 'name',
                'geojson': 'geojson',
                'populacao': 'population'}

def convert_names(datum):
    return {k: datum[v] for k, v in field_names.items()
            if not datum.get(v) == None}

def save(data, table='Localidade'):
    table_full_name = '"Municipio"."{}"'.format(table)
    sql_pattern = 'INSERT INTO {} ({}) VALUES ({})'

    join = lambda x: ', '.join(x)

    fields = field_names.keys()
    binds = map(lambda k: '%({})s'.format(k), fields)

    sql = sql_pattern.format(table_full_name, join(fields), join(binds))

    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as curr:
            curr.executemany(sql, map(convert_names, data))

    conn.close() # Context doesn't close connection

