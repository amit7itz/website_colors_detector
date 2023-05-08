#! /usr/bin/env python3
import sys
import io
import typing
import time

from PIL import Image
from collections import Counter
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from sty import bg, fg

import numpy

RUN_BROWSER_HEADLESS = True  # set to False to make the browser window is visible when running
PAGE_LOAD_WAIT_SECONDS = 5  # how much time to wait for the page to load
WINDOW_SIZE = "1366,768"

MINIMAL_VIBRANTNESS = 60  # colors under this vibrantness rating will be considered gray-scaled and eliminated from results 
MINIMAL_COLORS_DISTANCE = 55  # a color that its distance from another more frequent color is lower than the threshold will be eliminated from results
RESULT_COLORS_COUNT = 5
SORT_RESULTS_BY_VIBRANTNESS = False

def get_image_from_url(url: str) -> Image.Image:
    if not url.startswith("http"):
        url = "https://" + url
    
    options = ChromeOptions()
    if RUN_BROWSER_HEADLESS:
        options.add_argument("--headless=new")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument(f"--window-size={WINDOW_SIZE}")
    options.add_argument(f'--app={url}')
    with webdriver.Chrome(options=options) as driver:
        time.sleep(PAGE_LOAD_WAIT_SECONDS) # gives the browser time to load the page
        screenshot_bytes = driver.get_screenshot_as_png()
    return Image.open(io.BytesIO(screenshot_bytes))

def rgb2hex(r: int, g: int,b: int) -> str:
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def hex2rgb(hexcode: str) -> typing.Tuple[int]:
    return int(hexcode[-6:-4], 16), int(hexcode[-4:-2], 16), int(hexcode[-2:], 16)

def rgb_to_vibrantness(rgb: typing.Tuple[int]) -> int:
    return (max(rgb) - min(rgb))

def is_vibrant(rgb: typing.Tuple[int]) -> bool:
    return rgb_to_vibrantness(rgb) > MINIMAL_VIBRANTNESS

def colors_distance(color1: typing.Tuple[int], color2: typing.Tuple[int]) -> float:
    p1 = numpy.array(color1)
    p2 = numpy.array(color2)
    return numpy.linalg.norm(p1 - p2)

def get_unique_colors(colors: typing.List[typing.Tuple[int]], minimal_distance: int=MINIMAL_COLORS_DISTANCE, n: int=0) -> typing.List[typing.Tuple[int]]:
    unique_colors = []
    for color in colors:
        if all(map(lambda u: colors_distance(u, color) > minimal_distance, unique_colors)):
            unique_colors.append(color)
        if len(unique_colors) == n:
            break
    return unique_colors

def get_common_vibrant_colors_from_image(image: Image.Image) -> typing.List[typing.Tuple[int]]:
    width, height = image.size
    counter = Counter()
    colors = image.getcolors(width*height)
    for count, rgba in colors:
        rgb = rgba[:3]
        if is_vibrant(rgb):
            counter[rgb] = count
    return [rgb for rgb, _ in counter.most_common()]

def get_website_colors_from_image(image: Image.Image) -> typing.List[typing.Tuple[int]]:
    common_colors = get_common_vibrant_colors_from_image(image)
    common_colors = get_unique_colors(common_colors, n=RESULT_COLORS_COUNT)
    
    if SORT_RESULTS_BY_VIBRANTNESS:
        common_colors.sort(key=rgb_to_vibrantness, reverse=True)
    return common_colors[:RESULT_COLORS_COUNT]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f'''Run with a URL or DNS address, for example:\npython {sys.argv[0]} python.org''')
        exit(1)
        
    url = sys.argv[1]
    print(f"Taking a screenshot of {url}...")
    image = get_image_from_url(url)
    print(f"Calculating colors...")
    colors = get_website_colors_from_image(image)

    print("Most common colors are:")
    for color in colors:
        print(f'{bg(*color)}{fg.black}{rgb2hex(*color)}  {color}{fg.rs}{bg.rs}')