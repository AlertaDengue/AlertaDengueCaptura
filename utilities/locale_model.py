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
}

def names_converter(field_names):
    def convert_names(datum):
        return {k: datum[v] for k, v in field_names.items()
                if not datum.get(v) == None}
    return convert_names

def save(data, schema='Dengue_global', table='Municipio'):
    table_full_name = '"{}"."{}"'.format(schema, table)
    sql_pattern = 'INSERT INTO {} ({}) VALUES ({})'

    join = lambda x: ', '.join(x)

    fields = field_names[table].keys()
    binds = map(lambda k: '%({})s'.format(k), fields)

    sql = sql_pattern.format(table_full_name, join(fields), join(binds))

    convert_names = names_converter(field_names[table])

    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as curr:
            curr.executemany(sql, map(convert_names, data))

    conn.close() # Context doesn't close connection

