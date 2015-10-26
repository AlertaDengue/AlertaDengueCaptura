import psycopg2
from decouple import config

db_config = {
    'database': config('POSTGRES_DATABASE'),
    'user': config('POSTGRES_USER'),
    'password': config('POSTGRES_PASSWORD'),
    'host': config('POSTGRES_HOST'),
    'port': config('POSTGRES_PORT'),
}

# add double quotes to preserve case
field_names = {
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
}

def save(data):
    table = '"Municipio"."Clima_wu"'
    sql_pattern = 'INSERT INTO {} ({}) VALUES ({})'

    join = lambda x: ', '.join(x)

    data = {k: data[v] for k, v in field_names.items() if data.get(v)}
    fields = data.keys()
    binds = map(lambda k: '%({})s'.format(k), fields)

    sql = sql_pattern.format(table, join(fields), join(binds))

    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as curr:
            curr.execute(sql, data)

    conn.close() # Context doesn't close connection
