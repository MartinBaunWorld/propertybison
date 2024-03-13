from urllib.parse import urlparse, parse_qs
from utils import read, save, get_price

import scrapy


class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://www.imot.bg/pcgi/imot.cgi?act=3&slink=aehqhj&f1=1']

    def parse_property(self, response):
        print(f"Scraping property {response.url}")
        parsed_url = urlparse(response.url)
        iid = parse_qs(parsed_url.query).get("adv", "")[0]
        unit = read(f'results/{iid}.json', {})

        # TODO: remove title_en and desc_en if the bulgarian have changed
        unit.update({
                'id': iid,
                'images': ['https:' + it for it in response.css('#pictures_moving_details_small a::attr(data-link)').getall()],
                'price': get_price(response),
                'url': response.url.strip(),
                'location_bg': response.css('.location::text').get().strip(),
                'phone': response.css('.phone::text').get().strip(),
                "build_sq": response.css(".adParams strong::text").getall()[0],
                "floor": response.css(".adParams strong::text").getall()[1],
                'desc_bg': response.css("#description_div::text").get().strip(),
                'title_bg': response.css("title::text").get(),
        })

        save(f'results/{iid}.json', unit)

    def parse(self, response):
        for title in response.css('.photoLink'):
            url = 'https:' + title.css("a::attr(href)").get()
            if "adv=" in url:
                yield response.follow(url, callback=self.parse_property)

        for next_page in response.css(".pageNumbers::attr(href)"):
            yield response.follow("https:" + next_page.get(), self.parse)
