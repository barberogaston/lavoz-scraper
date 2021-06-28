import re

import scrapy


class LavozSpider(scrapy.Spider):
    name = 'lavoz'
    base_url = None
    page = 1

    def parse(self, response):
        xpath = '//div[contains(@class, "col-6 flex flex-wrap content-start sm-col-3 md-col-3 align-top")]/div[contains(@class, "relative")]/a[contains(@class, "text-decoration-none")]/@href'
        posting_urls = response.xpath(xpath).getall()
        yield from response.follow_all(posting_urls, self.parse_posting)

        xpath = '//a[contains(@aria-label, "Siguiente") and not(contains(@aria-disabled, "true"))]'
        next_page = response.xpath(xpath)

        if next_page:
            self.page += 1
            url = f'{self.base_url}&page={self.page}'
            yield scrapy.Request(url, callback=self.parse)

    def parse_posting(self, response):
        title = self.get_title(response)
        description = self.get_description(response)
        price = self.get_price(response)
        expenses = self.get_expenses(response)
        location = self.get_location(response)
        json = {
            'link': response.url,
            'title': title,
            'description': description,
            'expenses': expenses,
            'price': price,
            'location': location
        }
        yield json

    def get_title(self, response):
        xpath = '//h1[contains(@class, "h2 m0 mb0 bold line-height-1")]/text()'
        return response.xpath(xpath).get()

    def get_description(self, response):
        xpath = '//div[contains(@class, "col col-12 px1 md-px0 h4 ")]//text()'
        description = response.xpath(xpath).getall()
        if description == []:
            return None
        return ' '.join([d.replace('\n', '').strip() for d in description])

    def get_price(self, response):
        xpath = '//div[contains(@class, "h2 mt0 main bolder")]/text()'
        price = response.xpath(xpath).get()
        if not price:
            return None
        price = re.sub('[^0-9]', '', price)
        if price == '':
            return None
        return float(price)

    def get_expenses(self, response):
        xpath = '//h3[contains(@class, " h4 mt0 main bolder")]/text()'
        expenses = response.xpath(xpath).get()
        if not expenses:
            return None
        expenses = re.sub('[^0-9]', '', expenses)
        if expenses == '':
            return None
        return float(expenses)

    def get_location(self, response):
        xpath = '//p[contains(@class, "h4 bolder m0")]/text()'
        return response.xpath(xpath).get()
