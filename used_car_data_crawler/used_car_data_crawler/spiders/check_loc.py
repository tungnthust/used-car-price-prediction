import scrapy


class LocationSpider(scrapy.Spider):
    name = "location"
    start_urls = [
        'https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&radius=500'
    ]

    def parse(self, response):
        filename = f'location.html'
        with open(filename, 'wb') as f:
            f.write(response.body)