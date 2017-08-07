#PythonCrawler

### [DataBrowser](https://python-crawler-yahoo-tw.herokuapp.com/apps/yahooshoppingdata/browser/NewHotItem)

**userame/password: demo/demo**

### 1.Intro
Crawler that crawl all the ranking data from <https://tw.buy.yahoo.com>

Python module YahooCrawler crawl data with the following steps:

* Crawl ALL categories(main category called **zone**, subcatogy called **sub** ) from homepage
* Determinate which type of ranking to crawl
	* **Type 1**: called"**subs**" is the ranks show at every category links( http://tw.buy.yahoo.com/?sub=xxxx or z=xxx)
	![Imgur](http://i.imgur.com/cHsdFGy.png)
	* **Type 2**: called"**hotranknew**" which is the ranks shows at the bottem of homepage
	![Imgur](http://i.imgur.com/MAGRTWB.png)
	
* Save the items to db, ready for crawling the deatail info for every items
* After crawling deatail of every items, we got the following detailed :
	* Price
	* Original Price(建議售價)
	* Dicount rate (item price/orign price)
	* PictureURL
	* URL
	* Top ranking items related the item catogory
	* Description
* In the dash board, we can see every item detaild with thress kind of items(zone items, sub items, hot rank new items). We can easily analysis the item pricing trends and filter by specific dates, ranks, zone, sub name



### 2.TO DOs (Limitations)

* **Add Session Login**: Some category needs account & password login to see the items
* **Add Relation**: It's easiler for see the data with relations with all items and categories
* **Advanced Cralwering for item detail** : Some of the items have no price and suggest price in its product page, we need to crawl some other infos for this kind of products.
* **Push Notification on New Rank**: We can send push LINE/FB Messenger when ranking data changed
* **Put the python workers on Google Cloud**: So that we could run the crawler automatically and parallel 
* **Automatically generate the trending terms on evey catogries**



### 3.Installation

	pip install -r requirements.txt
	
##### Dependencies

* python 3.xx 
	* requests
	* beautifulsoup4
	* argparse
	* selenium
*chromedriver 

##### DB
I use parse app framework <https://github.com/parse-community/parse-server> host by <https://back4app.io>
DB is Mongo DB 

You can change the `parseServerheaders` and `parseRESTAPIBaseUrl` value in ./YahooCrawler/crawler.py if you host on another parse app URL





### 4.Usage

a. **Crawl Ranks Data**


	cd YahooCrawler	
	# List all categories ids
	python crawler.py -type list
	# For crawling type 1 subs 
	python crawler.py -type subs -index <zone start> <zone ends> -u <Yahoo Username> -p <Yahoo Password>

	# For crawling type 2 hotranknew 
	python crawler.py -type hotranknew

b. **Crawl Item Detail** 
	
	# For crawling eveyitem detailed on specific category 
	python crawler.py -type detailcrawl -iclass subItem  #Detail of subs items
	python crawler.py -type detailcrawl -iclass zoneItem #Detail of zone items
	python crawler.py -type detailcrawl -iclass NewHotItem #Detail of hotranknew items
![Imgur](http://i.imgur.com/QEySpFR.png)


c. **Analysis**
Open [DataBrowser](https://python-crawler-yahoo-tw.herokuapp.com/apps/yahooshoppingdata/browser/NewHotItem)
in the menu Browser > "subItem" or "NewHotItem" or "zoneItem"

![Imgur](http://i.imgur.com/tJi7m0R.png)
![Imgur](http://i.imgur.com/tQtLQ4m.png)

* Filter 

![Imgur](http://i.imgur.com/hiBBlpX.png)

* Export Data

![Imgur](http://i.imgur.com/CGn0nTQ.png)