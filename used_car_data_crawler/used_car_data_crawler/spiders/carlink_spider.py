import scrapy
import csv

class CarLinkSpider(scrapy.Spider):
    name = "carlink"

    start_urls = []
    with open('url_start_minivan.csv', newline='\n') as csvfile:
        links = csv.reader(csvfile, delimiter='\n')
        for row in links:
            start_urls.append(row[0])
            start_urls.append(row[0]+'&pagenumber=2')

    # start_urls = [
    #     'https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&radius=500&bodyType=Station%20Wagon',
    #     'https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&radius=500&bodyType=Station%20Wagon&pagenumber=2'
    # ]

    def parse(self, response):
        for item in response.xpath('//*[@id="main-content"]/div[3]/div[1]/div[1]/div/ul/li').getall():
            try:
                yield {
                    'link': 'https://www.edmunds.com'+scrapy.selector.Selector(text=item).xpath('body/li/div/div[2]/div/div[1]/div[1]/h2/a').attrib['href']
                }
            except:
                print("----------------------Skip----------------------")
        try:
            next_page = response.xpath('//*[@id="main-content"]/div[3]/div[1]/div[1]/div/div[2]/div[1]/a[2]').attrib['href']
            print(next_page)
            if next_page is not None:
                yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
        except:
            print("----------------------End----------------------")