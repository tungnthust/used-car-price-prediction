import scrapy
import re


class EmundsCrawlerSpider(scrapy.Spider):
    name = 'emunds_crawler'
    allowed_domains = ['www.edmunds.com']
    start_urls = ['https://www.edmunds.com/jeep/grand-cherokee/2021/vin/1C4RJEAG3MC601419/?radius=50']

    def parse(self, response):
        url = response.request.url.split('/')
        model = url[3]
        name = url[4].replace('-', ' ')
        released_year = int(url[5])

        overview = re.split(' \(|\)',
                            response.xpath('//*[@id="overview"]/section/div/div[1]/div[2]/span/text()').get()
                            )
        design_overview = overview[0].split('dr ')
        num_doors = int(design_overview[0][-1])
        edition = design_overview[0][:-2]
        car_type = design_overview[1]

        engine_overview = overview[1].split(' ')
        engine_capacity = float(engine_overview[0][:-1])
        num_cylinder = int(engine_overview[1][:-3])

        traveled_miles = int(
                            response.xpath('//*[@id="summary"]/section/div/ul[1]/li[1]/div[2]/text()').get()
                            .split(' ')[0].replace(',', '')
        )

        exterior_color = response.xpath('//*[@id="vin_exterior_color_swatch"]/span/@style').get().split(':')[1]
        interior_color = response.xpath('//*[@id="vin_interior_color_swatch"]/span/@style').get().split(':')[1]
        transmission = response.xpath('//*[@title="Transmission"]/parent::div/following-sibling::div/text()').get() \
            .split()[0]

        drive_train = response.xpath('//*[@title="Drivetrain"]/parent::div/following-sibling::div/text()').get()
        engine_type = response.xpath('//*[@title="Engine"]/parent::div/following-sibling::div/text()').get()
        horse_power = int(
            response.xpath('//*[@title="Horsepower"]/parent::div/following-sibling::div/text()').get().split()[0]
        )

        fuel_consumption = response.xpath('//*[@title="MPG"]/parent::div/following-sibling::div/text()').get()
        num_seats = int(
                response.xpath('//*[@title="Seats"]/parent::div/following-sibling::div/text()').get().split()[0]
        )

        num_accidents = int(
            response.xpath('//*[@id="history"]/section/div/ul/li[1]/div/div[2]/h3/text()').get().split()[0]
        )
        num_owners = int(
            response.xpath('//*[@id="history"]/section/div/ul/li[2]/div/div[2]/h3/text()').get().split()[0]
        )
        usage = response.xpath('//*[@id="history"]/section/div/ul/li[3]/div/div[2]/h3/text()').get()
        price = int(
            response.xpath('//*[@class="price-summary"]//*[contains(text(), "$")]/text()').get()[1:].replace(',', '')
        )

        options_cost = int(
                response.xpath('//*[contains(text(),"Total Value")]/parent::div/following-sibling::div/text()').get()[1:]
                .replace(',', '')
            )


        yield {
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
            'num_seats': num_seats,
            'num_accidents': num_accidents,
            'num_owners': num_owners,
            'usage': usage,
            'options_cost': options_cost,
            'price': price
        }
