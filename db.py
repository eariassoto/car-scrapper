from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.car_scrapper


def car_exists(id):
  row = db.cars.find_one({'_id': id})
  return True if row else False


def insert_car(car):
  result = db.cars.insert_one(car.__dict__)

