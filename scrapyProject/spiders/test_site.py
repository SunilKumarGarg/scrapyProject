import scrapy


class testSpider(scrapy.Spider):
    name = "test"

    def start_requests(self):
        urls = [
            'http://webscraper.io/test-sites/e-commerce/allinone'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for quote in response.css('div.thumbnail'):
            yield {
                'Name': quote.css('a.title::text').extract_first(),
                'Price': quote.css('h4.pull-right.price::text').extract_first(),
            }

        next_page = response.css('a.category-link::attr(href)').extract_first()
        print "next page" + next_page
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
