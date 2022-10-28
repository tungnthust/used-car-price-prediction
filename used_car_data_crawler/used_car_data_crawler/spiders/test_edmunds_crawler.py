import scrapy
from . import edmunds_crawler

class TestEdmundsCrawlerSpider(edmunds_crawler.EdmundsCrawlerSpider):
    name = 'test_edmunds_crawler'
    allowed_domains = ['edmunds.com']
    start_urls = ['https://www.edmunds.com/porsche/911/2018/vin/WP0AC2A97JS176957/?radius=500']

    def parse(self, response):
        yield response.follow(response.request.url,
                              callback=self.parse_data)