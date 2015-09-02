from postgres import Postgres
from decouple import config


db = Postgres(config('POSTGRES'))

field_names = {
    'Estacao_wu_estacao_id': 'station',
    "data_dia": 'date',
    "pressao_max": 'pressure_max',
    "pressao_med": 'pressure_mean',
    "pressao_min": 'pressure_min',
    "temp_max": 'temperature_max',
    "temp_med": 'temperature_mean',
    "temp_min": 'temperature_min',
    "umid_max": 'humidity_max',
    "umid_med": 'humidity_mean',
    "umid_min": 'humidity_min',
}

def save(data):
    table = '"Municipio"."Clima_wu"'
    sql_pattern = 'INSERT INTO {} ({}) VALUES ({})'

    join = lambda x: ', '.join(x)

    data = {k: data[v] for k, v in field_names.items() if data.get(v)}
    fields = map(lambda k: '"{}"'.format(k), data.keys())
    binds = map(lambda k: '%({})s'.format(k), data.keys())

    sql = sql_pattern.format(table, join(fields), join(binds))
    db.run(sql, data)
