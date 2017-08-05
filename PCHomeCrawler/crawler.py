# vim: set ts=4 sw=4 et: -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import re
import sys
import json
import requests
import argparse
import time
import codecs
from selenium import webdriver
from bs4 import BeautifulSoup
from six import u
from selenium import webdriver
import time

baseUrl="https://tw.buy.yahoo.com/"
__version__ = '1.0'
parseServerheaders = {'X-Parse-Application-Id':'Zq6vv931b0uypUjexa2LWBZW00JWE8esl6nj6oj1',
                      'X-Parse-REST-API-Key':'hRIlgb9yI7RUq7z0KgjOsBF3UfQokX7j5LFeFR0E',
                      'content-type': 'application/json'}

# if python 2, disable verify flag in requests.get()
VERIFY = True
if sys.version_info[0] < 3:
    VERIFY = False
    requests.packages.urllib3.disable_warnings()

class PCHomeCrawler(object):
    def __init__(self):
        ##request~
        url="https://tw.buy.yahoo.com/"
        res = requests.get(baseUrl)
        new_text=re.sub(r"(\n\s*<!--\n\s*<)|(\n\s*-->\n\s*<)","\n<",res.text)
        #print(new_text)
        soup=BeautifulSoup(new_text, "html.parser")
        zoneResultList,sidList, zidList= [],[],[]
        zonelist=soup.select("li[zid]")
        for zone in zonelist:
            sublist=zone.select("li[sid]")
            subs=[]
            for sub in sublist:
                sidList.append(int(sub['sid']))
                subs.append({"subname":sub.get_text().replace('\n',''),"sid":sub['sid']})
            zoneResultList.append({"zone":zone.select("a.yui3-menu-label")[0].text,"subs":subs,"zid":zone['zid']})
            zidList.append(zone['zid'])
        #print(zoneResultList)
        print(len(zonelist))
        print(zidList)
        print(sorted(sidList))
        listnum=0
        for zone in zoneResultList:
            print('\n'+zone["zone"])
            zoneUrl=baseUrl+"?z="+zone['zid'].split('z')[1]
            self.crawlData(self,zoneUrl,'zone',zone['zone'],zone['zid'])
            for sub in zone['subs']:
                print(listnum)
                listnum+=1
                subUrl=baseUrl+"?sub="+sub['sid']
                print('\n'+sub["subname"])
                self.crawlData(self,subUrl,'sub',zone['zone'],zone['zid'],sub["subname"],int(sub['sid']))
            time.sleep(0.05)
    @staticmethod
    def saveItem(saveClass,data):
        url = 'https://parseapi.back4app.com/classes/'+saveClass 
        r = requests.post(url, data=json.dumps(data), headers=parseServerheaders)
        time.sleep(0.01)
        return r.text
    @staticmethod
    def crawlData(self,url,classType,zoneName,zid,subName=0,subId=0):
        rs=requests.get(url)
        bs=BeautifulSoup(rs.text, "html.parser")
        bestList=bs.select("#cl-hotrank .pdset")
        for idx,item in enumerate(bestList):
            print(item.select('.pic')[0].a['href'])
            intro=item.select('.intro')[0]
            print(intro.select('.text')[0].text,
                  intro.select('.text')[0].a['href'],
                  intro.select('.red-price')[0].text)
            data={    "picHref" : item.select('.pic')[0].a['href'],
                      "zoneName":zoneName,
                      "zoneId":zid,
                      "itemName":intro.select('.text')[0].text,
                      "url":intro.select('.text')[0].a['href'],
                      "price":int(intro.select('.red-price')[0].text),
                      "detailCrawled":False,
                      "rank":idx+1
                  }
            #print('subId',subId)
            if subId>0:
                data['subId']=subId
                data['subName']=subName
            print(json.dumps(data))
            
            print(self.saveItem(classType+"Item",data))

if __name__ == '__main__':
    c = PCHomeCrawler()
