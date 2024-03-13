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


def get_price(response):
    try:
        txt = response.css("#cena::text").get().strip()
        txt = txt.replace(" ", "")
        if 'EUR' in txt:
            return int(txt.split('EUR')[0].strip()) * 2
        
        return int(txt.split('BGN')[0].strip())
    except:
        return 0
