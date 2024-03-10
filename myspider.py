import scrapy
from json import dumps, dump, load
import pathlib

from os import listdir, path
import os
from openai import OpenAI
from sys import argv
from jinja2 import Template
from urllib.parse import urlparse, parse_qs


def read(fn, default=None):
    if not os.path.exists(fn) and default is not None:
        return default

    with open(fn, "r") as f:
        return load(f)


def save(fn, o):
    with open(fn, "w") as f:
        return dump(o, f, indent=2)


client = OpenAI()
def chatgpt(msg):
    return client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", 'content': msg}],
    ).choices[0].message.content


def trans():
    for fn in listdir("results"):
        unit = read(f"results/{fn}")

        if 'desc_en' in unit:
            continue

        print(f'Translating {fn}')

        unit['desc_en'] =  chatgpt("translate the following from potentially bulgarian to english " + unit['desc_bg'])
        unit['title_en'] =  chatgpt("translate the following from potentially bulgarian to english " + unit['title_bg'])
        unit['location_en'] =  chatgpt("translate the following from potentially bulgarian to english " + unit['location_bg'])
        
        save(f"results/{fn}", unit)

"""
"""

tmpl = Template("""---
title: "{{title_en}}"
image: "{{image}}"
description: "{{desc}}"
---

location: {{location_en}}

build: {{build_sq}}

phone: {{phone}}

floor: {{floor}}

{{desc_en}}

{% for image in images[1:] %}
![{{ image}}]( {{image }})

{% endfor %}

""")

def blog():
    for fn in listdir("results"):
        unit = read(f"results/{fn}")
        pathlib.Path(f'content/en/bulgaria').mkdir(parents=True, exist_ok=True)

        with open(f'content/en/bulgaria/{unit["id"]}.md', 'w') as f:
            f.write(
                tmpl.render(
                    title_en=unit.get('title_en', unit.get('title_bg')).replace(":: imot.bg Advertisment", "").replace("\"", "'").replace("\n", " "),
                    desc_en=unit.get('desc_en', unit.get('desc_bg')),
                    image=unit.get('images')[0] if len(unit.get('images'))>0 else "",
                    floor=unit.get('floor'),
                    phone=unit.get('phone'),
                    build_sq=unit.get('build_sq'),
                    images=unit.get('images'),
                    location_en=unit.get("location_en"),
                    desc=unit.get('desc_en', unit.get('desc_bg')).replace("\n", "").replace("\"", "'"),
            ))



def get_price(response):
    try:
        txt = response.css("#cena::text").get().strip()
        txt = txt.replace(" ", "")
        if 'EUR' in txt:
            return int(txt.split('EUR')[0].strip()) * 2
        
        return int(txt.split('BGN')[0].strip())
    except:
        return 0


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


if __name__ == "__main__" and argv[1] == 'trans':
    trans()

if __name__ == "__main__" and argv[1] == 'blog':
    blog()
