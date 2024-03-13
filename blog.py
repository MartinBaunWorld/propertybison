import scrapy
from json import dumps, dump, load
import pathlib

from os import listdir, path
import os
from openai import OpenAI
from sys import argv
from jinja2 import Template
from urllib.parse import urlparse, parse_qs

from utils import read, save


tmpl = Template("""---
title: "{{title_en}}"
image: "{{image}}"
description: "{{desc}}"
tags: {{tags}}
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
                    tags=dumps(unit.get('tags', [])),
                    build_sq=unit.get('build_sq'),
                    images=unit.get('images'),
                    location_en=unit.get("location_en"),
                    desc=unit.get('desc_en', unit.get('desc_bg')).replace("\n", "").replace("\"", "'"),
            ))


if __name__ == "__main__":
    blog()
