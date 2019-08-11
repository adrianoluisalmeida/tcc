import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
import unicodedata
from scrapy.utils.project import get_project_settings

from yahoo.items import YahooItem


class FinancesSpider(CrawlSpider):
    name = "finances"
    start_urls = ["https://br.financas.yahoo.com/industries/Telecomunicacoes-Tecnologia"]

    def parse(self, response):
        body_sel = Selector(response)
        urls_eventos = body_sel.xpath(
            "//div[@class='Ovx(a)']//table//tbody//td[@class='data-col0 Ta(start) Pstart(6px) Pend(15px)']//a//@href").extract()

        for url in urls_eventos:
            yield Request("https://br.financas.yahoo.com" + url, self.parse_atracao)

    def to_str(self, selector):
        return selector.extract()[0].encode("utf-8")

    def parse_atracao(self, response):
        item = YahooItem()
        item['code'] = response.url.split("p=")[1]
        item['price'] = response.xpath("//div[@id='quote-market-notice']/../..//span/text()")[0].extract()
        yield item


