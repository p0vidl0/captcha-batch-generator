# Inspired by https://github.com/mbi/django-simple-captcha

import os
import random
import itertools

from PIL import Image, ImageDraw, ImageFont

try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

CAPTCHA_LETTER_ROTATION = (-35, 35)
CAPTCHA_BACKGROUND_COLOR = "#ffffff"
CAPTCHA_FOREGROUND_COLOR = "#001100"
CAPTCHA_FONT_SIZE = 22
CAPTCHA_IMAGE_SIZE = None
CAPTCHA_FONT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "fonts/Vera.ttf"))
CAPTCHA_PUNCTUATION = """_"',.;:-"""
DISTANCE_FROM_TOP = 4


def noise_arcs(draw, image):
    size = image.size
    draw.arc([-20, -20, size[0], 20], 0, 295, fill=CAPTCHA_FOREGROUND_COLOR)
    draw.line(
        [-20, 20, size[0] + 20, size[1] - 20], fill=CAPTCHA_FOREGROUND_COLOR
    )
    draw.line([-20, 0, size[0] + 20, size[1]], fill=CAPTCHA_FOREGROUND_COLOR)
    return draw

def noise_dots(draw, image):
    size = image.size
    for p in range(int(size[0] * size[1] * 0.1)):
        draw.point(
            (random.randint(0, size[0]), random.randint(0, size[1])),
            fill=CAPTCHA_FOREGROUND_COLOR,
        )
    return draw

def post_smooth(image):
    from PIL import ImageFilter

    return image.filter(ImageFilter.SMOOTH)

CAPTCHA_NOISE_FUNCTIONS = (noise_dots,)
CAPTCHA_FILTER_FUNCTIONS = (post_smooth,)

def _callable_from_string(string_or_callable):
    if callable(string_or_callable):
        return string_or_callable
    else:
        return getattr(
            __import__(".".join(string_or_callable.split(".")[:-1]), {}, {}, [""]),
            string_or_callable.split(".")[-1],
        )

def noise_functions():
    if CAPTCHA_NOISE_FUNCTIONS:
        return map(_callable_from_string, CAPTCHA_NOISE_FUNCTIONS)
    return []


def filter_functions():
    if CAPTCHA_FILTER_FUNCTIONS:
        return map(_callable_from_string, CAPTCHA_FILTER_FUNCTIONS)
    return []


def getsize(font, text):
    if hasattr(font, "getoffset"):
        return tuple([x + y for x, y in zip(font.getsize(text), font.getoffset(text))])
    else:
        return font.getsize(text)

def makeimg(size):
    if CAPTCHA_BACKGROUND_COLOR == "transparent":
        image = Image.new("RGBA", size)
    else:
        image = Image.new("RGB", size, CAPTCHA_BACKGROUND_COLOR)
    return image

def captcha_image(text, scale=1):
    fontpath = CAPTCHA_FONT_PATH

    if fontpath.lower().strip().endswith("ttf"):
        font = ImageFont.truetype(fontpath, CAPTCHA_FONT_SIZE * scale)
    else:
        font = ImageFont.load(fontpath)

    if CAPTCHA_IMAGE_SIZE:
        size = CAPTCHA_IMAGE_SIZE
    else:
        size = getsize(font, text)
        size = (size[0] * 2, int(size[1] * 1.4))

    image = makeimg(size)
    xpos = 2

    charlist = []
    for char in text:
        if char in CAPTCHA_PUNCTUATION and len(charlist) >= 1:
            charlist[-1] += char
        else:
            charlist.append(char)
    for char in charlist:
        fgimage = Image.new("RGB", size, CAPTCHA_FOREGROUND_COLOR)
        charimage = Image.new("L", getsize(font, " %s " % char), "#000000")
        chardraw = ImageDraw.Draw(charimage)
        chardraw.text((0, 0), " %s " % char, font=font, fill="#ffffff")
        if CAPTCHA_LETTER_ROTATION:
            charimage = charimage.rotate(
                random.randrange(*CAPTCHA_LETTER_ROTATION),
                expand=0,
                resample=Image.BICUBIC,
            )
        charimage = charimage.crop(charimage.getbbox())
        maskimage = Image.new("L", size)

        maskimage.paste(
            charimage,
            (
                xpos,
                DISTANCE_FROM_TOP,
                xpos + charimage.size[0],
                DISTANCE_FROM_TOP + charimage.size[1],
            ),
        )
        size = maskimage.size
        image = Image.composite(fgimage, image, maskimage)
        xpos = xpos + 2 + charimage.size[0]

    if CAPTCHA_IMAGE_SIZE:
        # centering captcha on the image
        tmpimg = makeimg(size)
        tmpimg.paste(
            image,
            (
                int((size[0] - xpos) / 2),
                int((size[1] - charimage.size[1]) / 2 - DISTANCE_FROM_TOP),
            ),
        )
        image = tmpimg.crop((0, 0, size[0], size[1]))
    else:
        image = image.crop((0, 0, xpos + 1, size[1]))
    draw = ImageDraw.Draw(image)

    for f in noise_functions():
        draw = f(draw, image)
    for f in filter_functions():
        image = f(image)

    out = StringIO()
    if len(text) == 3 :
        if text == 'AUX':
            text = '_AUX'
        elif text == 'COM':
            text = '_COM'
        elif text == 'CON':
            text = '_CON'
        elif text == 'PRN':
            text = '_PRN'
    image.save('images/' + text + '.png', "PNG")
    out.seek(0)

    return text
