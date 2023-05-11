# Website colors detector
A tool to extract the most common vibrant colors from any website. The algorithm is useful for automatic personalization features, for example adjusting the color palette of your website for each client by the color palette of their brand's website.

![Alt text](assets/screenshot.png?raw=true)

# How it works
Here is the script's algorithm step-by-step:
1. Open the URL on a Chrome browser using Selenium and take a screenshot.
2. Count how many times each color appears on the image.
3. Eliminate colors that are considered "non-vibrant", meaning that are too close to gray-scale colors. The vibrantness level of a specific color is calculated by the difference between the highest color channel to the lowest one. `max(r, g, b) - min(r, g, b)`
4. Sort the colors by their commonness.
5. Eliminate colors that are too close to another more frequent color. The distance is an Euclidean distance as if the colors are points on a three-dimensional space.
6. Return the 5 most frequent colors.

# Customization
There are several constants within the script that can be adjusted to alter the results, such as the minimal vibrantness of the colors and the minimal distance between colors.

# How to install
1. Install the packages in requirements.txt
```
pip install -r requirements.txt
```
2. Install Chrome's web driver

# License
MIT License
