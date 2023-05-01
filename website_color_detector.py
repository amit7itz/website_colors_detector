from PIL import Image
from collections import Counter
import glob
from selenium import webdriver
import io
import PIL.PngImagePlugin
import typing
import time

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def hex2rgb(hexcode):
    return int(hexcode[-6:-4], 16), int(hexcode[-4:-2], 16), int(hexcode[-2:], 16)

def is_vibrant(pixel):
    return (max(pixel) - min(pixel)) > 60

def get_website_colors_from_image(image: PIL.PngImagePlugin.PngImageFile) -> typing.List[str]:
    pix = image.load()
    width, height = image.size
    c = Counter()
    for line in range(height):
        for column in range(width):
            color = pix[column, line][:3]
            if is_vibrant(color):
                c[color] += 1
    common_colors = c.most_common()[:5]
    return [color for color, _ in common_colors]

if __name__ == "__main__":
    url = "https://beerandbeyond.com/"
    if not url.startswith("http"):
        url = "https://" + url
    # Set up the webdriver
    driver = webdriver.Chrome()
    try:
        driver.maximize_window()
        driver.get(url)
        time.sleep(3) # gives the browser time to fully load the page
        screenshot_bytes = driver.get_screenshot_as_png()
    finally:
        driver.quit()

    image: PIL.PngImagePlugin.PngImageFile = Image.open(io.BytesIO(screenshot_bytes))
    colors = get_website_colors_from_image(image)

    for color in colors:
        print(rgb2hex(*color), color)