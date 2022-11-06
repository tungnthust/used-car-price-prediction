import time
from shutil import which

import scrapy
import re
from . import utils
from selenium import webdriver

class EdmundsCrawlerSpider(scrapy.Spider):
    name = 'edmunds_crawler'

    origin = 'https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&radius=500&price='
    allowed_domains = ['www.edmunds.com']
    start_urls = ['https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&radius=500&price=0-10000']
    # driver = webdriver.Firefox(executable_path="C:/Users/Lenovo/Desktop/ML/geckodriver-v0.32.0-win64/geckodriver.exe")

    def parse(self, response):
        for i in range(0, 100):
            # Small step size (2000) for price = 0 - 40,000
            if i < 4:
                for j in range(5):
                    yield response.follow(self.origin + f'{j*2000+i*10000+1}-{(j+1)*2000 + i*10000}',
                                          callback=self.parse_list)
            else:
                yield response.follow(self.origin + f'{i * 10000 + 1}-{(i + 1) * 10000}',
                                      callback=self.parse_list)

    def parse_list(self, response):
        count = response.css('span.inventory-count::text').get()
        if int(count.replace(',', '')) > 0:
            for item in response.xpath('//*[@id="main-content"]/div[3]/div[1]/div[1]/div/ul/li').getall():
                try:
                    link = 'https://www.edmunds.com'+scrapy.selector.Selector(text=item).xpath('body/li/div/div[2]/div/div[1]/div[1]/h2/a').attrib['href']

                    yield response.follow(link,
                                          callback=self.parse_data)
                except:
                    print("----------------------Skip----------------------")
            try:
                next_page = response.xpath('//*[@aria-label="Next Listing Page"]').attrib['href']
                if next_page is not None:

                    yield scrapy.Request(response.urljoin(next_page), callback=self.parse_list)
            except:
                print("----------------------End----------------------")

    def parse_data(self, response):
        url_str = response.request.url
        url = url_str.split('/')
        vin_id = url[7]
        model = url[3]
        name = url[4].replace('-', ' ')
        released_year = int(url[5])
        self.driver.get(url_str)
        time.sleep(1)
        try:
            view_more_info_button = self.driver.find_element('xpath',
                                                             '//*[contains(@class, "options-and-packages")]/button')
            view_more_info_button.click()
        except:
            pass

        try:
            button = self.driver.find_element('xpath', '//*[contains(@data-subaction-name, "view_features")]')
            button.click()
        except:
            try:
                view_more_info_button = self.driver.find_element('xpath', '//*[contains(@class, "features-and-specs")]/button')
                view_more_info_button.click()
                button = self.driver.find_element('xpath', '//*[contains(@data-subaction-name, "view_features")]')
                button.click()
            except:
                pass

        response = scrapy.selector.Selector(text=self.driver.page_source.encode('utf-8'))
        try:
            overview_str = response.xpath('//*[@id="overview"]/section/div/div[1]/div[2]/span/text()').get()
            overview = re.split(' \(|\)', overview_str)
        except:
            overview_str = ''
            overview = []
        car_type = None
        edition = None
        num_doors = None
        if 'dr' in overview_str:
            design_overview = overview[0].split('dr ')
            num_doors = int(design_overview[0][-1])
            try:
                edition = design_overview[0][:-2]
            except:
                pass
            for type_ref in utils.CAR_TYPE:
                if type_ref in design_overview[1]:
                    car_type = type_ref
                    break
        else:
            car_type_index = 0
            for type_ref in utils.CAR_TYPE:
                if type_ref in overview_str:
                    car_type = type_ref
                    car_type_index = overview_str.index(type_ref)
                    break
            edition = overview_str[:(car_type_index-1)]

        engine_capacity = None
        num_cylinder = None

        if len(overview) > 1:
            engine_overview = overview[1].split(' ')
            for item in engine_overview:
                if 'L' in item:
                    engine_capacity = float(item[:-1])
                if 'cyl' in item:
                    num_cylinder = int(item[:-3])
        try:
            traveled_miles = int(
                                response.xpath('//*[@id="summary"]/section/div/ul[1]/li[1]/div[2]/text()').get()
                                .split(' ')[0].replace(',', '')
            )
        except:
            traveled_miles = None
        try:
            exterior_color = response.xpath('//*[@id="vin_exterior_color_swatch"]/span/@style').get().split(':')[1]
        except:
            exterior_color = None
        try:
            interior_color = response.xpath('//*[@id="vin_interior_color_swatch"]/span/@style').get().split(':')[1]
        except:
            interior_color = None
        try:
            transmission = response.xpath('//*[@title="Transmission"]/parent::div/following-sibling::div/text()').get() \
                .split()[0]
        except:
            transmission = None

        try:
            electric_range = float(response.xpath('//*[@title="Electric range"]/parent::div/following-sibling::div/text()').get() \
                            .split('mi')[0])
        except:
            electric_range = None

        try:
            electric_charge_time = float(response.xpath('//*[@title="Electric charge time"]/parent::div/following-sibling::div/text()').get() \
                            .split('hr')[0])
        except:
            electric_charge_time = None

        try:
            drive_train = response.xpath('//*[@title="Drivetrain"]/parent::div/following-sibling::div/text()').get()
        except:
            drive_train = None
        try:
            engine_type = response.xpath('//*[@title="Engine"]/parent::div/following-sibling::div/text()').get()
        except:
            engine_type = None
        try:
            horse_power = int(
                response.xpath('//*[@title="Horsepower"]/parent::div/following-sibling::div/text()').get().split()[0]
            )
        except:
            horse_power = None

        try:
            fuel_consumption = response.xpath('//*[@title="MPG"]/parent::div/following-sibling::div/text()').get()
        except:
            fuel_consumption = None

        try:
            num_seats = int(
                    response.xpath('//*[@title="Seats"]/parent::div/following-sibling::div/text()').get().split()[0]
            )
        except:
            num_seats = None

        try:
            num_accidents = int(
                response.xpath('//*[@id="history"]/section/div/ul/li[1]/div/div[2]/h3/text()').get().split()[0]
            )
        except:
            num_accidents = None
        try:
            num_owners = int(
                response.xpath('//*[@id="history"]/section/div/ul/li[2]/div/div[2]/h3/text()').get().split()[0]
            )
        except:
            num_owners = None
        try:
            usage = response.xpath('//*[@id="history"]/section/div/ul/li[3]/div/div[2]/h3/text()').get()
        except:
            usage = None
        try:
            price = int(
                response.xpath('//*[@class="price-summary"]//*[contains(text(), "$")]/text()').get()[1:].replace(',', '')
            )
        except:
            price = None
        try:
            options_cost = int(
                    response.xpath('//*[contains(text(),"Total Value")]/parent::div/following-sibling::div/text()').get()[1:]
                    .replace(',', '')
                )
        except:
            options_cost = 0

        features = response.xpath('//*[contains(@class, "modal-content")]/div/ul/li/span/text()').getall()
        if len(features) == 0:
            features = response.xpath(
                '//*[contains(@class, "features-and-specs")]/div/div/div/ul/li/text()').getall()

        output = {
            'vin_id': vin_id,
            'model': model,
            'name': name,
            'released_year': released_year,
            'type': car_type,
            'edition': edition,
            'num_doors': num_doors,
            'engine_capacity': engine_capacity,
            'num_cylinder': num_cylinder,
            'traveled_miles': traveled_miles,
            'exterior_color': exterior_color,
            'interior_color': interior_color,
            'transmission': transmission,
            'drive_train': drive_train,
            'engine_type': engine_type,
            'horse_power': horse_power,
            'fuel_consumption': fuel_consumption,
            'electric_range': electric_range,
            'electric_charge_time': electric_charge_time,
            'num_seats': num_seats,
            'num_accidents': num_accidents,
            'num_owners': num_owners,
            'usage': usage,
            'features': features,
            'options_cost': options_cost,
            'price': price,
            'url': url_str
        }

        yield output
