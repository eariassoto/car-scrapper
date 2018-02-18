#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2018 Emmanuel Arias
# ariassotoemmanuel@gmail.com

from requests import post, get
from lxml import html
from re import search, sub, findall
from bs4 import BeautifulSoup

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


def parse_car_equipment_from_rows(rows):
  car_equipment_list = []
  for row in rows:
    columns = row.find_all("td")
    if len(columns) == 2 and 'width' in columns[1].attrs and columns[1].attrs['width'] == '316':
      equipment = columns[1].find("font").contents[0]
      car_equipment_list.append(clean_input(equipment))
  return car_equipment_list


def parse_car_attributes_from_rows(rows):
  car_attributes_map = {}
  for row in details_table_rows:
    columns = row.find_all("td")
    if len(columns) == 3:
      key = columns[1].find("font").contents[0]
      value = columns[2].find("font")
      if value:
        value = value.contents[0]
      else:
        value = columns[2].find("img").attrs['src']
      car_attributes_map[clean_input(key)] = clean_input(value)
  return car_attributes_map


# sending get request and saving the response as response object
seach_results_page = post(url=URL, data=make_request_payload(500), headers=headers)
seach_results_body = BeautifulSoup(seach_results_page.text, 'html.parser')
total_pages = get_last_page_from_body(seach_results_body)

print("Total pages found: " + total_pages)

link = get_car_links_from_body(seach_results_body)[0]

print("Scraping data from: " + link)

id = get_car_id_from_link(link)
print("ID: " + id)

car_details_page = get(url=link, headers=headers)
car_details_body = BeautifulSoup(car_details_page.text, 'html.parser')

car_title = get_car_title_from_page(car_details_body)
print(car_title)

details_table_rows = get_rows_from_page(car_details_body)
car_attributes_map = parse_car_attributes_from_rows(details_table_rows)
car_equipment_list = parse_car_equipment_from_rows(details_table_rows)
car_imgs = parse_car_images_from_rows(details_table_rows)

print("Car's attributes:")
print(car_attributes_map)
print("Car's equipment:")
print(car_equipment_list)
print("Car images:")
print(car_imgs)
