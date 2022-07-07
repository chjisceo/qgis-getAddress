# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import requests
import time
from urllib import parse
from urllib.parse import quote
import json


def getInfo(url): # get html infos from URL
    request = requests.get(url, verify = False)

    return request


def getNaddr(n_request): # Get address from NAVER
    # Get Address coordinate
    dir_txt = "https://map.naver.com/v5/directions/-/" # text includes coordinates about address.
    dir_idx = n_request.text.find(dir_txt)+len(dir_txt) # cut start text
    # request.text[dir_idx:dir_idx+100].find("/-/")

    dir_end_idx = n_request.text[dir_idx:dir_idx+100].find("/-/") + dir_idx -2
    addr_data = n_request.text[dir_idx:dir_end_idx].split(",")
    # e.g) 14135340.4917805,4518369.290700372,서울특별시 중구 을지로1가 46-2
    return addr_data


def getNpoi(n_request): # Get POIs from NAVER
    # POI Part
    # find __APOLLO_STATE__ to get POI
    txt = "__APOLLO_STATE__ = "
    idx = n_request.text.find(txt)
    idx_end = n_request.text[idx:].find("$ROOT_QUERY.nxPlaces")

    poi_data = n_request.text[idx + len(txt):idx + idx_end - 2] + "}"

    if len(poi_data) > 5: # If exist POIs then make dict format.
        poi_dict = json.loads(poi_data)
        return poi_dict
    else:
        return False


def getKdata(k_request):
    # KAKAO part

    # find __shapeData__
    txt = "shapeData\\"
    idx = k_request.text.find(txt)-1

    idx_end = k_request.text[idx:].find("relatedAddressListSize")
    part_geom = k_request.text[idx:idx+idx_end-3]
    part_geom = part_geom.replace('\\','')
    part_geom = "{"+part_geom+"}"
    dict = json.loads(part_geom)

    # check shape data None or Exist
    if dict['shapeData'] is not None:
        dict['POLYGON'] = dict['shapeData'][:dict['shapeData'].find('!^')]
        dict['POLYGON'] = dict['POLYGON'].replace(","," ")
        dict['POLYGON'] = dict['POLYGON'].replace("|", ",")
        dict['POLYGON'] = "POLYGON ((" + dict['POLYGON'] + "))"

    # TEST FOR QGIS
    make_wkt = "POINT({} {})".format(dict['wx'],dict['wy'])
    # print(make_wkt)
    dict['POINT'] = make_wkt

    return dict
# idx_2_end = request.text[idx+idx_end+1:idx+200].find(",")
#
#
# x = request.text[idx+38:idx+idx_end]
# y = request.text[idx+idx_end+1:idx+idx_end+idx_2_end+1]

# full = requests.get(url, allow_redirects=True,verify_ssl=False).url
target = '서울특별시 중구 을지로1가 46-2'

addr = quote(target) # Address to target

k_url = "https://search.daum.net/search?nil_suggest=btn&w=tot&DA=SBC&q={}".format(addr)
n_url = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={}".format(addr)

# 'https://map.naver.com/v5/directions/-/14143145.99183594,4509838.867708068,서울특별시 강남구 테헤란로63길 9,,/-/ca'


n_request = getInfo(n_url)
k_request = getInfo(k_url)

n_poi = getNpoi(n_request)
n_addr = getNaddr(n_request)

k_data = getKdata(k_request)