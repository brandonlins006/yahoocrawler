# vim: set ts=4 sw=4 et: -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import re,json,time,codecs,sys
import requests
import argparse
from bs4 import BeautifulSoup

baseUrl="https://tw.buy.yahoo.com/"
__version__ = '1.0'
parseServerheaders = {'X-Parse-Application-Id':'Zq6vv931b0uypUjexa2LWBZW00JWE8esl6nj6oj1',
                      'X-Parse-REST-API-Key':'hRIlgb9yI7RUq7z0KgjOsBF3UfQokX7j5LFeFR0E',
                      'content-type': 'application/json'}
parseRESTAPIBaseUrl="https://parseapi.back4app.com/"
# if python 2, disable verify flag in requests.get()
VERIFY = True
if sys.version_info[0] < 3:
    VERIFY = False
    requests.packages.urllib3.disable_warnings()

class PCHomeCrawler(object):
    def __init__(self,cmdline=None):
        ##request~
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='''
            Crawler for buy.yahoo.tw  
            Input: Type
            Output: To Parse DB
        ''')
        parser.add_argument('-type', metavar='CrawlerType', help='TYPE hotranknew/subs/list/detailcrawl ', required=True)
        parser.add_argument('-index', metavar=('START_INDEX', 'END_INDEX'), type=int, nargs=2, help="Start and end index for zones")
        parser.add_argument('-list', metavar='List', help="List all zones and subs")
        parser.add_argument('-iclass', metavar='DetailClass', help="The Detail Class to Crawl")
        if cmdline:
            args = parser.parse_args(cmdline)
        else:
            args = parser.parse_args()

        url="https://tw.buy.yahoo.com/"
        res = requests.get(baseUrl)
        new_text=re.sub(r"(\n\s*<!--\n\s*<)|(\n\s*-->\n\s*<)","\n<",res.text)
        #print(new_text)
        soup=BeautifulSoup(new_text, "html.parser")
        zoneResultList,sidList, zidList,subsToZone = [], [], [],{}
        zonelist=soup.select("li[zid]")
        for zone in zonelist:
            subs=[]
            for sub in zone.select("li[sid]"):
                sidList.append(int(sub['sid']))
                subs.append({"subname":sub.get_text().replace('\n',''),"sid":sub['sid']})
                subsToZone[int(sub['sid'])]={'zid':zone['zid'],'zone':zone.select("a.yui3-menu-label")[0].text}
            zoneResultList.append({"zone":zone.select("a.yui3-menu-label")[0].text,"subs":subs,"zid":zone['zid']})
            zidList.append(zone['zid'])
        if args.type=="list" :
            print('Zone Number:',len(zonelist),'\n','ZoneIDs',zidList,'\n','SubIDs',sorted(sidList))
        elif args.type=="hotranknew":
            timestamp = int(time.time())
            #first time for get the valid subs those have ranking data
            requestsAPIBase=baseUrl+"catalog/ajax/recmdHotNew?segmentId=999999&t="+str(timestamp)+"&subId="
            r=requests.get(requestsAPIBase+json.dumps(sorted(sidList)).replace('[','').replace(']',''))
            rs=json.loads(r.text)['billboard']
            validSubIdList=rs['subId'].split(",")
            for smallSublist in [validSubIdList[i:i+10] for i in range(0, len(validSubIdList), 10)]:
                urlString=json.dumps(smallSublist).replace('[','').replace(']','').replace('"','')
                r=requests.get(requestsAPIBase+urlString)
                rs=json.loads(r.text)['billboard']
                labels,smallSubIds=[item['label'] for item in rs['tabs']+rs['othertab']],rs['subId'].split(",")
                rankDataList=[]
                for idx,subitems in enumerate(rs['panels']):
                    subid,subname=int(smallSubIds[idx]),labels[idx]
                    zoneName,zid=subsToZone[subid]['zone'],subsToZone[subid]['zid']
                    rankDataList.append(self.crawlHotRankNewItem(self,subitems['mainitem'],zoneName,zid,subname,subid))
                    for item in subitems['pditem']:
                        rankDataList.append(self.crawlHotRankNewItem(self,item,zoneName,zid,subname,subid))
                self.batchUploadItem(rankDataList,'NewHotItem','create')
        elif args.type=="subs":
            print("subs")
            if args.index and args.index[0]>=0:
                start = args.index[0]
                end = start if args.index[1]<start else args.index[1]
            else:
                start,end=0,len(zidList)-1
            for idx,zone in enumerate(zoneResultList):
                if idx<start:
                    continue
                if idx>=end:
                    break
                print('\n'+zone["zone"])
                zoneUrl=baseUrl+"?z="+zone['zid'].split('z')[1]
                self.crawlData(self,zoneUrl,'zone',zone['zone'],zone['zid'])
                for sub in zone['subs']:
                    subUrl=baseUrl+"?sub="+sub['sid']
                    print('\n'+sub["subname"])
                    self.crawlData(self,subUrl,'sub',zone['zone'],zone['zid'],sub["subname"],int(sub['sid']))
        elif args.type=="detailcrawl":
            className=args.iclass if args.iclass else 'NewHotItem'
            print('crawlering the item detail of the class...', className)
            results=json.loads(self.getUncrawledItems(className))['results']
            updateDataList=[]
            for idx,item in enumerate(results):
                print(idx,item['itemName'])
                updateData=self.crawlSingleItem(baseUrl+item['url'].replace(baseUrl,""),item['price'])
                updateData['objectId']=item['objectId']
                updateDataList.append(updateData)
            self.batchUploadItem(updateDataList,className,'update')    
        else:
            print('you have the wrong type')
    @staticmethod
    def batchUploadItem(dataList,className,opType):
        print('uplodaing data to parse server..',opType)
        for listpart in [dataList[i:i+50] for i in range(0, len(dataList), 50)]:
            requestDatas=[]
            for data in listpart:
                if opType=='update':
                    reqData={
                        "method":"PUT",
                        "path":"classes/"+className+'/'+data['objectId'] 
                    }
                    data.pop('objectId')
                    reqData["body"]=data
                elif opType=='create':
                    reqData={
                        "method":"POST",
                        "path":"classes/"+className
                    }
                    reqData["body"]=data
                requestDatas.append(reqData)
            partBody={"requests":requestDatas}
            url = parseRESTAPIBaseUrl+'batch' 
            r = requests.post(url, data=json.dumps(partBody), headers=parseServerheaders)
            print(r.text)
        return 0
    @staticmethod
    def crawlSingleItem(url,price):
        bs=BeautifulSoup(requests.get(url).text,"html.parser")
        updateData={}
        if(len(bs.select('#cl-mainitem'))):
            mainitem=bs.select('#cl-mainitem')[0]
            updateData['suggestPrice']=mainitem.select('.suggest .price')[0].get_text().replace('$','').replace(',','') if len(mainitem.select('.suggest .price')) else ""
            updateData['desc']=mainitem.select('.desc-list')[0].get_text() if len(mainitem.select('.desc-list')) else ""
            updateData['price']=mainitem.select('.priceinfo .price')[0].get_text().replace('$','').replace(',','') if len(mainitem.select('.priceinfo .price')) else price
            updateData['discount']=str(int(updateData['price'])/int(updateData['suggestPrice'])) if updateData['suggestPrice']!='' else ''
        updateData['relationItems']=','.join([item.get_text() for item in bs.select('#cl-ordrank .yui3-u-1.desc')]) 
        updateData['detailCrawled']=True
        return  updateData
    @staticmethod
    def getUncrawledItems(className):
        url = parseRESTAPIBaseUrl+'classes/'+className 
        r = requests.get(url, params={'where':json.dumps({"detailCrawled":False}),'limit':1000}, headers=parseServerheaders)
        return r.text
    @staticmethod
    def crawlHotRankNewItem(self,pditem,zoneName,zid,subName,subId):
        price =BeautifulSoup(pditem['price'], "lxml").get_text().replace('$','')
        data={
            "picHref" : pditem['pdimg'],
            "zoneName":zoneName,
            "zoneId":zid,
            "pid":pditem['pdid'],
            "itemName":pditem['desc'],
            "url":pditem['url'],
            "price":price,
            "detailCrawled":False,
            "rank":int(pditem['hpp'].split('item')[1]),
            "subId":subId,
            "subName":subName
        }
        print(data['itemName'],data['price'])
        return data
    @staticmethod
    def saveItem(saveClass,data):
        url = parseRESTAPIBaseUrl+'classes/'+saveClass 
        r = requests.post(url, data=json.dumps(data), headers=parseServerheaders)
        return r.text
    @staticmethod
    def crawlData(self,url,classType,zoneName,zid,subName=0,subId=0):
        rs=requests.get(url)
        bs=BeautifulSoup(rs.text, "html.parser")
        bestList=bs.select("#cl-hotrank .pdset")
        saveDataList=[]
        for idx,item in enumerate(bestList):
            intro=item.select('.intro')[0]
            print(intro.select('.text')[0].text)
            data={    "picHref" : item.select('.pic')[0].a['href'],
                      "zoneName":zoneName,
                      "zoneId":zid,
                      "itemName":intro.select('.text')[0].text,
                      "url":intro.select('.text')[0].a['href'],
                      "price":intro.select('.red-price')[0].text ,
                      "detailCrawled":False,
                      "rank":idx+1
                  }
            if subId>0:
                data['subId']=subId
                data['subName']=subName
            saveDataList.append(data)
        self.batchUploadItem(saveDataList,classType+"Item",'create')
        return 0

if __name__ == '__main__':
    PCHomeCrawler()
