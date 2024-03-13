import scrapy
from json import dumps, dump, load
import pathlib

from os import listdir, path
import os
from openai import OpenAI
from sys import argv
from jinja2 import Template
from urllib.parse import urlparse, parse_qs

from utils import read, save, chatgpt


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


if __name__ == "__main__":
    trans()
