# Website color detector
A tool to extract the most common vibrant colors from any website, useful for understanding what are the main brand colors of a certain organization.

![Alt text](assets/screenshot.png?raw=true)

# How to it works
1. The script opens the URL on a Chrome browser using Selenium and takes a screenshot.
2. Count how many times each color appears on the image.
3. Eliminate all colors that are considered "non-vibrant", meaning that is too close to gray-scale colors. The vibrantness level of a specific color is calculated by the difference maximum color channel to the minimum one. `max(r, g, b) - min(r, g, b)`
4. Sort the colors by their frequency.
5. Eliminate all colors that are too close to another more frequent color. The distance is an Euclidean distance as if the colors are points on a three-dimensional space.
6. Returns the 5 most frequent colors.

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