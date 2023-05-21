import re

import scrapy


class LavozSpider(scrapy.Spider):
    name = 'lavoz'
    base_url = None
    page = 1

    def parse(self, response):
        carousel_xpath = "//div[contains(@class, 'super_destacado_carousel')]/following-sibling::div/div/a[contains(@class, 'btn-primary')]/@href"
        all_postings_xpath = "//a[contains(@target, '_self')]/@href"

        xpath = f"{carousel_xpath}|{all_postings_xpath}"
        posting_urls = response.xpath(xpath).getall()
        yield from response.follow_all(posting_urls, self.parse_posting)

        xpath = '//a[contains(@aria-label, "Siguiente") and not(contains(@aria-disabled, "true"))]'

        if response.xpath(xpath):
            self.page += 1
            url = f'{self.base_url}&page={self.page}'
            yield scrapy.Request(url, callback=self.parse)

    def parse_posting(self, response):
        title = self.get_title(response)
        description = self.get_description(response)
        price = self.get_price(response)
        location = self.get_location(response)
        yield {
            'link': response.url,
            'title': title,
            'description': description,
            'price': price,
            'location': location
        }

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
