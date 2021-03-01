import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from schrodersch.items import Article


class SchroderschSpider(scrapy.Spider):
    name = 'schrodersch'
    start_urls = ['https://www.schroders.com/de/ch/asset-management/insights/']

    def parse(self, response):
        links = response.xpath('//div[@class="row insight-section "]//div[@class="col-xs-12"]/a/@href').getall()
        links = [link.lower() for link in links]
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="next "]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@itemprop="headline"]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="date hidden-xs hidden-sm show-print"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@id="mainBody"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
