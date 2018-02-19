#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2018 Emmanuel Arias
# ariassotoemmanuel@gmail.com

from requests import post, get
from lxml import html
from re import search, sub, findall
from bs4 import BeautifulSoup
from datetime import date

# api-endpoint
URL = "http://crautos.com/rautosusados/searchresults.cfm"

headers = {
    'Refer': 'http://crautos.com/rautosusados/',
    'content-type': 'application/x-www-form-urlencoded',
  }
  
template_payload = {
  'brand': '00',
  'modelstr': '',
  'style': '00',
  'fuel': '0',
  'trans': '0',
  'financed': '00',
  'province': '0',
  'doors': '0',
  'yearfrom': '1960',
  'yearto': '2018',
  'pricefrom': '100000',
  'priceto': '200000000',
  'orderby': '0',
  'lformat': '0',
  'p': '500'
}


def make_request_payload(page_number):
  request_payload = template_payload.copy()
  request_payload['p'] = page_number
  return request_payload


def get_last_page_from_body(body):
  last_page_btn = body.find_all("button", string="Última Página >>")
  last_page_a = last_page_btn[0].parent
  a_href = last_page_a.get('href')
  return a_href[14:-2]


def get_car_id_from_link(link):
  id = search('=\d+&', link)
  return id.group(0)[1:-1]


def get_car_links_from_body(body):
  links = []
  cars = body.find_all("a", class_="inventory")
  for car in cars:
    car_link = car.get('href')
    car_link = car_link.replace('cardetail', "economicos-useddetail2")
    car_link = "http://crautos.com/usados/" + car_link
    links.append(car_link)
  return links


def get_car_title_from_page(page):
  title_table = page.find("table", width="423")
  return title_table.find('b').contents[0]


def get_rows_from_page(page):
  details_table = page.find("table", width="525")
  return details_table.find_all('tr')


def clean_input(input):
  input = input.replace('\r','')
  input = input.replace('\t','')
  input = input.replace('\n','')
  input = sub(' +',' ', input)
  input = input.strip()
  return input


def parse_car_images_from_rows(rows):
  car_imgs = []
  for row in rows:
    columns = row.find_all("td")
    if len(columns) == 1:
      img_div = columns[0].find("div")
      if img_div:
        imgs = img_div.find_all("img")
        for i in imgs:
          car_imgs.append('http://crautos.com' + i.attrs['src'])
  return car_imgs


def clean_column_data(column):
  data = column.find("font").contents[0]
  data = clean_input(data)
  return data


def parse_car_equipment_from_rows(rows):
  car_equipment_list = []
  for row in rows:
    columns = row.find_all("td")
    if len(columns) == 2 and 'width' in columns[1].attrs and columns[1].attrs['width'] == '316':
      equipment = clean_column_data(columns[1])
      car_equipment_list.append(equipment)
  return car_equipment_list


def parse_is_car_registered_value(value_column):
  value = clean_column_data(value_column)
  if value == "SI":
    return True
  else:
    return False


def parse_numeric_attribute(value_column):
  value = clean_column_data(value_column)
  return int(value)


def parse_car_cost(value_column):
  value = clean_column_data(value_column)
  value = search('(\d+,?)+(.\d+)?', value).group(0)
  value = value.replace(',', '')
  return int(value)


def parse_car_mileage(value_column):
  value = clean_column_data(value_column)
  value = search('(\d+)+(.\d+)?', value)
  if value:
    return int(value.group(0))
  else:
    return None


def parse_car_date(value_column):
  value = clean_column_data(value_column)
  numbers = findall('\d+', value)
  months = {
    'Enero':1,
    'Febrero':2,
    'Marzo':3,
    'Abril':4,
    'Mayo':5,
    'Junio':6,
    'Julio':7,
    'Agosto':8,
    'Setiembre':9,
    'Octubre':10,
    'Noviembre':11,
    'Diciembre':12
  }
  month = ''
  for m in months:
    if m in value:
      month = months[m]
  return date(int(numbers[1]), month, int(numbers[0]))


def parse_car_engine_displacement(value_column):
  value = clean_column_data(value_column)
  value = search('(\d+,?)+', value).group(0)
  value = value.replace(',', '')
  return int(value)


def get_translated_key(key):
  translation_dict = {u'Estado:' : 'state',
    u'Est\xe1 inscrito:' : 'is_registered',
    u'Estilo:' : 'style',
    u'Marca:' : 'brand',
    u'Color Exterior:' : 'outer_color',
    u'# de puertas:' : 'number_doors',
    u'Modelo:' : 'model',
    u'Nombre:' : 'seller_name',
    u'Cilindrada:' : 'displacement',
    u'Precio:' : 'price',
    u'A\xf1o:' : 'year',
    u'Transmisi\xf3n:' : 'transmission',
    u'Color Interior:' : 'inner_color',
    u'Provincia:' : 'province',
    u'Kilometraje:' : 'mileage',
    u'Tel\xe9fono:' : 'seller_phone',
    u'Ingres\xf3:' : 'post_date',
    u'Combustible:' : 'fuel'
  }
  return translation_dict[key]


def parse_car_attribute(key_column, value_column):
  key = clean_column_data(key_column)
  key = get_translated_key(key)
  if key ==  'is_registered':
    value = parse_is_car_registered_value(value_column)
  elif key == 'seller_phone':
    value = value_column.find("img").attrs['src']
    value = clean_input(value)
    value = 'http://crautos.com' + value
  elif key == 'year':
    value = parse_numeric_attribute(value_column)
  elif key == 'price':
    value = parse_car_cost(value_column)
  elif key == 'mileage':
    value = parse_car_mileage(value_column)
  elif key == 'post_date':
    value = parse_car_date(value_column)
  elif key == 'displacement':
    value = parse_car_engine_displacement(value_column)
  elif key == 'number_doors':
    value = parse_numeric_attribute(value_column)
  else:
    value = clean_column_data(value_column)
  return key, value


def parse_car_attributes_from_rows(rows):
  car_attributes_map = {}
  for row in rows:
    columns = row.find_all("td")
    if len(columns) == 3:
      key, value = parse_car_attribute(columns[1], columns[2])
      car_attributes_map[key] = value
  return car_attributes_map


class CarRecord:
    id = 0
    title = ''
    link = ''
    attributes = {}
    equipment = []
    images = []

    def __init__(self, id, title, link, attributes, equipment, images):
      self.id = id
      self.link = link
      self.title = title
      self.attributes = attributes
      self.equipment = equipment
      self.images = images

    def Print(self):
      print('Title: ' + self.title)
      print('Id: ' + str(self.id))
      print('Link: ' + self.link)
      print('Attributes: ' + str(self.attributes))
      print('Equipment: ' + str(self.equipment))
      print('Images: ' + str(self.images))


def scrap_car_data(link):
  print("Scraping data from: " + link)

  id = get_car_id_from_link(link)

  car_details_page = get(url=link, headers=headers)
  car_details_body = BeautifulSoup(car_details_page.text, 'html.parser')
  car_title = get_car_title_from_page(car_details_body)

  details_table_rows = get_rows_from_page(car_details_body)
  car_attributes_map = parse_car_attributes_from_rows(details_table_rows)
  car_equipment_list = parse_car_equipment_from_rows(details_table_rows)
  car_imgs = parse_car_images_from_rows(details_table_rows)

  car = CarRecord(id, car_title, link, car_attributes_map, car_equipment_list, car_imgs)
  return car


# sending get request and saving the response as response object
seach_results_page = post(url=URL, data=make_request_payload(500), headers=headers)
seach_results_body = BeautifulSoup(seach_results_page.text, 'html.parser')
total_pages = get_last_page_from_body(seach_results_body)

print("Total pages found: " + total_pages)

car_links = get_car_links_from_body(seach_results_body)

for link in car_links:
  car = scrap_car_data(link)
  car.Print()
