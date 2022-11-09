import scrapy
from . import edmunds_crawler

class TestEdmundsCrawlerSpider(edmunds_crawler.EdmundsCrawlerSpider):
    name = 'test_edmunds_crawler'
    allowed_domains = ['edmunds.com']
    start_urls = ['https://www.edmunds.com/toyota/4runner/2022/vin/JTEKU5JR0N6019543/?radius=500']

    def parse(self, response):
        yield response.follow(response.request.url,
                              callback=self.parse_data)