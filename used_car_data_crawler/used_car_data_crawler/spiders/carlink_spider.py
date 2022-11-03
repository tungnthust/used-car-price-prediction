import scrapy
from selenium import webdriver
from shutil import which
from selenium.webdriver.common.keys import Keys


class CarLinkSpider(scrapy.Spider):
    name = "carlink"
    origin = 'https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&bodyType=SUV&radius=500&price='
    allowed_domains = ['www.edmunds.com']
    start_urls = [origin+'0-10000']
    driver = webdriver.Firefox(executable_path=which('geckodriver.exe'))

    def parse(self, response):
        for i in range(0, 100):
            # Small step size (2000) for price = 0 - 40,000
            if i < 4:
                for j in range(5):
                    yield response.follow(self.origin + f'{j*2000+i*10000+1}-{(j+1)*2000 + i*10000}',
                                          callback=self.parse_link)
                    yield response.follow(self.origin + f'{j * 2000 + i * 10000 + 1}-{(j + 1) * 2000 + i * 10000}'+'&pagenumber=2',
                                          callback=self.parse_link)
            else:
                yield response.follow(self.origin + f'{i * 10000 + 1}-{(i + 1) * 10000}',
                                      callback=self.parse_link)
                yield response.follow(self.origin + f'{i * 10000 + 1}-{(i + 1) * 10000}'+'&pagenumber=2',
                                      callback=self.parse_link)

    def parse_link(self, response):
        self.driver.get(response.request.url)
        input_location = self.driver.find_element('xpath', '//*[contains(@aria-label, "Near ZIP")]')
        for i in range(5):
            input_location.send_keys(Keys.BACK_SPACE)
        input_location.send_keys('14564')
        input_location.send_keys(Keys.ENTER)
        response = scrapy.selector.Selector(text=self.driver.page_source.encode('utf-8'))
        count = response.css('span.inventory-count::text').get()
        if int(count.replace(',', '')) > 0:
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
                    yield scrapy.Request(response.urljoin(next_page), callback=self.parse_link)
            except:
                print("----------------------End----------------------")