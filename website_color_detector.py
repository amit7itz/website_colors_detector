#! /usr/bin/env python3
"""
Detects and prints the most common vibrant colors of a website
Example:
python website_color_detector.py https://python.org
"""
import sys
import io
import collections

from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from sty import bg
from PIL import Image

import numpy

RUN_BROWSER_HEADLESS = True  # set to False to make the browser window is visible when running
PAGE_LOAD_TIMEOUT_SECONDS = 10  # how much time to wait for the page to load
WINDOW_SIZE = "1366,768"

# colors under this vibrantness rating will be considered gray-scaled and eliminated from results
MINIMAL_VIBRANTNESS = 60
# a color that its distance from another more frequent color is lower than the threshold will be eliminated from results
MINIMAL_COLORS_DISTANCE = 55
RESULT_COLORS_COUNT = 5
SORT_RESULTS_BY_VIBRANTNESS = False

RGB = tuple[int, int, int]


def get_image_from_url(url: str) -> Image.Image:
    """
    Returns a screenshot of the website
    """
    if not url.startswith("http"):
        url = "https://" + url

    options = ChromeOptions()
    if RUN_BROWSER_HEADLESS:
        options.add_argument("--headless=new")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument(f"--window-size={WINDOW_SIZE}")
    options.add_argument(f'--app={url}')
    with webdriver.Chrome(options=options) as driver:
        WebDriverWait(driver, PAGE_LOAD_TIMEOUT_SECONDS).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )
        screenshot_bytes = driver.get_screenshot_as_png()
    return Image.open(io.BytesIO(screenshot_bytes))


def rgb2hex(r: int, g: int, b: int) -> str:
    """
    Converts an (r, g, b) color to hex color format "#RRGGBB"
    """
    return f"#{r:02x}{g:02x}{b:02x}"


def hex2rgb(hexcode: str) -> RGB:
    """
    Converts hex color format "#RRGGBB" to (r, g, b)
    """
    return int(hexcode[-6:-4], 16), int(hexcode[-4:-2], 16), int(hexcode[-2:], 16)


def rgb_to_vibrantness(rgb: RGB) -> int:
    """
    Returns the vibrantness rating of a given color
    """
    return (max(rgb) - min(rgb))


def is_vibrant(rgb: RGB) -> bool:
    """
    Returns whether a given color is vibrant (above the minimal vibrantness threshold)
    """
    return rgb_to_vibrantness(rgb) > MINIMAL_VIBRANTNESS


def colors_distance(color1: RGB, color2: RGB) -> float:
    """
    Returns the euclidean distance between the two colors as if they are points on a three-dimensional space
    """
    p1 = numpy.array(color1)
    p2 = numpy.array(color2)
    return float(numpy.linalg.norm(p1 - p2))


def get_unique_colors(colors: list[RGB],
                      n: int = 0,
                      minimal_distance: int = MINIMAL_COLORS_DISTANCE) -> list[RGB]:
    """Given a list of colors, returns a new list of the "unique" colors,
    eliminating colors that are closer than the minimal distance to another previous color.

    :param colors: a list of colors
    :type colors: list[RGB]
    :param n: maximal number of colors to return, defaults to 0 (no limit)
    :type n: int, optional
    :param minimal_distance: minimal euclidean distance between unique colors, defaults to MINIMAL_COLORS_DISTANCE
    :type minimal_distance: int, optional
    :return: A list of unique colors
    :rtype: list[RGB]
    """
    unique_colors: list[RGB] = []
    for color in colors:
        # pylint: disable=cell-var-from-loop
        if all(map(lambda u: colors_distance(u, color) >= minimal_distance, unique_colors)):
            unique_colors.append(color)
        if len(unique_colors) == n:
            break
    return unique_colors


def get_common_vibrant_colors_from_image(image: Image.Image) -> list[RGB]:
    """
    Given an image, returns all the colors that are vibrant sorted from the most frequent to the least
    """
    width, height = image.size
    counter: collections.Counter = collections.Counter()
    colors = image.getcolors(width*height)
    for count, rgba in colors:
        rgb = rgba[:3]
        if is_vibrant(rgb):
            counter[rgb] = count
    return [rgb for rgb, _ in counter.most_common()]


def get_website_colors_from_image(image: Image.Image) -> list[RGB]:
    """
    Returns the most frequent unique vibrant colors from a website screenshot
    """
    common_colors = get_common_vibrant_colors_from_image(image)
    common_colors = get_unique_colors(common_colors, n=RESULT_COLORS_COUNT)
    if SORT_RESULTS_BY_VIBRANTNESS:
        common_colors.sort(key=rgb_to_vibrantness, reverse=True)
    return common_colors[:RESULT_COLORS_COUNT]


def main():  # pylint: disable=missing-function-docstring
    if len(sys.argv) != 2:
        print(f'''Run with a URL or DNS address, for example:\npython {sys.argv[0]} python.org''')
        exit(1)

    url = sys.argv[1]
    print(f"Taking a screenshot of {url}...")
    image = get_image_from_url(url)
    print("Processing colors...")
    colors = get_website_colors_from_image(image)

    print("Most common colors are:")
    for color in colors:
        print(f' - {bg(*color)}  {bg.rs} {rgb2hex(*color)} {color}')


if __name__ == "__main__":
    main()
