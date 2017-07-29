import scrapy
import json


class testConfigSpider(scrapy.Spider):

    name = "testConfig" #This is the name of testConfigSpider
    
    """
    Spider is run using Command"scrapy crawl testConfig -o test.json -a sitemap=config.json"
    result is saved in TabErrort.json
    sitemap is passed as argument in form of json file config.json
    This is the format of config.json:

    {
        "siteMap":[
                    {
                        "href":"http://webscraper.io/test-sites/e-commerce/allinone",                        
                        "ItemContainer":"div.thumbnail",
                        "Item": 
                        {
                            "Name":"a.title::text",
                            "Price":"h4.pull-right.price::text"
                        },
                        "Repeat":"No"
                    },
                    {
                        "href":"a.category-link::attr(href)",
                        "ItemContainer":"div.thumbnail",
                        "Item": 
                        {
                            "Name":"a.title::text",
                            "Price":"h4.pull-right.price::text"
                        },
                        "Repeat":"Yes" #keep looking for this href in each page till not found. Then go to next item.
                    },
                    {
                        "href":"http://webscraper.io/test-sites/e-commerce/allinone/computers/tablets",
                        "ItemContainer":"div.thumbnail",
                        "Item": 
                        {
                            "Name":"a.title::text",
                            "Price":"h4.pull-right.price::text"
                        },
                        "Repeat":"No"
                    }
                ]
        }

    """

    def scrapNextPage(self, next_page, response):    

        """
        if next page is valid and not visited yet, scrap it.
        if next page is not valid or already visited, Go to next element in sitemap and try to scrap it.
        """
        
        if next_page is not None and not response.urljoin(next_page) in self.visitedURL:
            return response.follow(next_page, callback=self.parse)
        else:

            self.ProcessedSiteMap = self.ProcessedSiteMap + 1     

            if self.ProcessedSiteMap  < self.lenSiteMap:
                self.currentDict = self.sitemap[self.ProcessedSiteMap]
                next_page = self.getNextPage(response)
                return self.scrapNextPage(next_page, response)

    def getSiteMap(self):

        """
        get the config file name from sitemap attribute and load it.
        """
        sitemapFile = getattr(self,'sitemap',None)

        with open(sitemapFile) as sitemap_file:    
            #This contains array of all sitemap element
            self.sitemap = json.load(sitemap_file)["siteMap"]

        self.lenSiteMap = len(self.sitemap) #Total element in sitemap
        self.ProcessedSiteMap = 0   #Number of elements already processed


    

    def gotoNextSiteMapIfNoRepeat(self):

        if self.currentDict["Repeat"] != "Yes":            
            self.ProcessedSiteMap = self.ProcessedSiteMap + 1 
            if self.ProcessedSiteMap  < self.lenSiteMap:
                self.currentDict = self.sitemap[self.ProcessedSiteMap]

    def getNextPage(self, response):
        if "http://" in self.currentDict["href"]:
            return self.currentDict["href"]
        else:
            return response.css(self.currentDict["href"]).extract_first()


    def start_requests(self):

        #Read the sitemap configuration
        self.getSiteMap()

        #keep track of all the page visited
        self.visitedURL = []

        if self.lenSiteMap <= 0:
            return #if there is no sitemap in configuration file, return

        urls = [
            self.sitemap[0]["href"] #Take first element from sitemap as starting point. Scrap start from this page
        ]

        
        #CurrentDict stores the data of the sitemap element from configuration file that is being processed right now
        self.currentDict = self.sitemap[0] 

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        #This function is called once for each scraped page. Keep track of all the page visited.
        self.visitedURL.append(response.url)
        print self.visitedURL

        #Scrap all item data from the current page
        data = {}
        for quote in response.css(self.currentDict["ItemContainer"]):
            for k in self.currentDict["Item"].keys():                
                data[k] = quote.css(self.currentDict["Item"][k]).extract_first()              
            yield data

        self.gotoNextSiteMapIfNoRepeat()

        next_page = self.getNextPage(response)        

        yield self.scrapNextPage(next_page, response)
            
            
