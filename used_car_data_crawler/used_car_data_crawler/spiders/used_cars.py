import scrapy
import csv

class UsedCarsSpider(scrapy.Spider):
    name = 'used_cars'
    origin = 'https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&radius=500&bodyType=Minivan&price='
    allowed_domains = ['www.edmunds.com']
    start_urls = ['https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&radius=500&bodyType=Minivan&price=0-10000']
    total = 0
    f = open("./url_start_minivan.csv", 'w',newline='')
    writer = csv.writer(f)

    def parse(self, response):
        for i in range(0, 100):
            # Small step size (2000) for price = 0 - 40,000
            if i < 4:
                for j in range(5):
                    yield response.follow(self.origin + f'{j*2000+i*10000+1}-{(j+1)*2000 + i*10000}', callback=self.parse_count)
            else:
                yield response.follow(self.origin + f'{i * 10000 + 1}-{(i + 1) * 10000}',
                                      callback=self.parse_count)

    #     for link in response.css('a.usurp-inventory-card-vdp-link::attr(href)'):
    #         yield response.follow(self.origin + link.get(), callback=self.parse_used_car_data)
    #
    def parse_count(self, response):
        min_value = response.css('input[aria-label="Min Price value"]::attr(value)').get()
        max_value = response.css('input[aria-label="Max Price value"]::attr(value)').get()
        count = response.css('span.inventory-count::text').get()
        self.total += int(count.replace(',', ''))
        yield {
            f'{min_value}-{max_value}': count
        }
        if int(count.replace(',', '')) > 0:
            self.writer.writerow([response.request.url])
        print(f'Total: {self.total}')



