from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError

field_names = {
    "DateUTC": 'date',
    "Pressao_max": 'pressure_max',
    "Pressao_med": 'pressure_mean',
    "Pressao_min": 'pressure_min',
    "Tmax": 'temperature_max',
    "Tmed": 'temperature_mean',
    "Tmin": 'temperature_min',
    "Umid_max": 'humidity_max',
    "Umid_med": 'humidity_mean',
    "Umid_min": 'humidity_min',
}

def save(data):
    mongo = MongoClient()
    db = mongo.clima
    coll = db[data['station']]

    data = {k: data[v] for k, v in field_names.items() if data.get(v)}

    coll.create_index([("DateUTC", ASCENDING),], unique=True, dropDups=True)

    try:
        return coll.insert(data, w=1)
    except DuplicateKeyError:
        print("{} already in the database.".format(data['date']))

