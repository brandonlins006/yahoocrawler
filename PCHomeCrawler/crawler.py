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
        zoneResultList=[]
        zonelist=soup.select("li[zid]")
        sidList=[]
        zidList=[]
        for zone in zonelist:
            sublist=zone.select("li[sid]")
            subs=[]
            for sub in sublist:
                sidList.append(int(sub['sid']))
                subs.append({"subname":sub.get_text().replace('\n',''),"sid":sub['sid']})
            zoneResultList.append({"zone":zone.select("a.yui3-menu-label")[0].text,"subs":subs,"zid":zone['zid']})
            zidList.append(zone['zid'])
        print(zoneResultList)
        print(len(zonelist))
        print(zidList)
        print(sorted(sidList))
        listnum=0
        for zone in zoneResultList:
            print('\n'+zone["zone"])
            zoneUrl=baseUrl+"?z="+zone['zid'].split('z')[1]
            rzs=requests.get(zoneUrl)
            bsZone=BeautifulSoup(rzs.text, "html.parser")
            zoneBestList=bsZone.select("#cl-hotrank .pdset")
            for item in zoneBestList:
                print(item.select('.pic')[0].a['href'])
                intro=item.select('.intro')[0]
                print(intro.select('.text')[0].text,
                      intro.select('.text')[0].a['href'],
                      intro.select('.red-price')[0].text)
            for sub in zone['subs']:
                print(listnum)
                listnum+=1
                subUrl=baseUrl+"?sub="+sub['sid']
                print('\n'+sub["subname"])
                rss=requests.get(subUrl)
                bsSub=BeautifulSoup(rss.text, "html.parser")
                subBestList=bsSub.select("#cl-hotrank .pdset")
                for item in subBestList:
                    print(item.select('.pic')[0].a['href'])
                    intro=item.select('.intro')[0]
                    print(intro.select('.text')[0].text,
                          intro.select('.text')[0].a['href'],
                          intro.select('.red-price')[0].text)
            time.sleep(0.05)


if __name__ == '__main__':
    c = PCHomeCrawler()
