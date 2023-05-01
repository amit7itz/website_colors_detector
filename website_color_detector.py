from PIL import Image
from collections import Counter
import glob
from selenium import webdriver
import io
import PIL.PngImagePlugin
import typing
import time
import numpy

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def hex2rgb(hexcode):
    return int(hexcode[-6:-4], 16), int(hexcode[-4:-2], 16), int(hexcode[-2:], 16)

def is_vibrant(pixel):
    return (max(pixel) - min(pixel)) > 60

def colors_distance(color1: typing.Tuple[int], color2: typing.Tuple[int]) -> float:
    p1 = numpy.array(color1)
    p2 = numpy.array(color2)
    return numpy.linalg.norm(p1 - p2)

def remove_similar_colors(colors: typing.List[typing.Tuple[int]]):
    unique_colors = []
    for color in colors:
        if all(map(lambda u: colors_distance(u, color) > 20, unique_colors)):
            unique_colors.append(color)
    return unique_colors

def get_website_colors_from_image(image: PIL.PngImagePlugin.PngImageFile) -> typing.List[str]:
    pix = image.load()
    width, height = image.size
    c = Counter()
    for count, rgba in image.getcolors(image.size[0]*image.size[1]):
        color = rgba[:3]
        if is_vibrant(color):
            c[color] = count
    common_colors = [color for color, _ in c.most_common()[:5]]
    common_colors = remove_similar_colors(common_colors)
    return common_colors

def get_image_from_url(url: str) -> PIL.PngImagePlugin.PngImageFile:
    if not url.startswith("http"):
        url = "https://" + url
    
    driver = webdriver.Chrome()
    try:
        driver.maximize_window()
        driver.get(url)
        time.sleep(3) # gives the browser time to fully load the page
        screenshot_bytes = driver.get_screenshot_as_png()
    finally:
        driver.quit()

    return Image.open(io.BytesIO(screenshot_bytes))

if __name__ == "__main__":
    url = "https://beerandbeyond.com/"
    
    image = get_image_from_url(url)
    colors = get_website_colors_from_image(image)

    for color in colors:
        print(rgb2hex(*color), color)