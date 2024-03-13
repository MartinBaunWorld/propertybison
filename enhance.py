from json import loads
from os import listdir, path

from utils import read, save, chatgpt


def enhance():
    for fn in sorted(listdir("results")):
        print(f'Checking.. results/{fn}')
        unit = read(f"results/{fn}")

        if 'tags' in unit:
            continue

        if unit.get('desc_en', '').strip() == '':
            print("skipping")
            continue

        print(f'Enhancing.. results/{fn}')

        print("from this property description please make a json format with agencyName,  bedrooms, bathrooms, yardSq, tags.\n\n" + unit['desc_en'])
        print(chatgpt("from this property description please make a json format with agencyName,  bedrooms, bathrooms, yardSq, tags.\n\n" + unit['desc_en']))
        unit.update(loads(chatgpt("from this property description please make a json format with agencyName,  bedrooms, bathrooms, yardSq, tags.\n\n" + unit['desc_en'])))
    
        save(f"results/{fn}", unit)


if __name__ == "__main__":
    enhance()
