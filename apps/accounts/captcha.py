"""图形验证码生成（基于 Pillow，无额外依赖）。"""
import random
import string

from django.conf import settings
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 去除容易混淆的字符 0/O、1/I/L
CODE_CHARS = "".join(c for c in (string.ascii_uppercase + string.digits)
                     if c not in "0O1IL")


def _load_font(size):
    for font_path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def generate_captcha_code(length=4):
    return "".join(random.choices(CODE_CHARS, k=length))


def generate_captcha_image(code):
    """根据验证码文字生成 PNG 图片的二进制内容。"""
    width = getattr(settings, "ACCOUNTS_CAPTCHA_WIDTH", 130)
    height = getattr(settings, "ACCOUNTS_CAPTCHA_HEIGHT", 44)

    image = Image.new("RGB", (width, height), (245, 247, 250))
    draw = ImageDraw.Draw(image)

    # 背景噪点
    for _ in range(120):
        pos = (random.randint(0, width - 1), random.randint(0, height - 1))
        draw.point(pos, fill=(random.randint(120, 200),) * 3)

    # 干扰线
    for _ in range(4):
        points = [(random.randint(0, width), random.randint(0, height))
                  for _ in range(2)]
        draw.line(points, fill=tuple(random.randint(90, 170) for _ in range(3)),
                  width=1)

    font = _load_font(28)
    # 逐字绘制，随机颜色、位置、旋转
    char_width = width // (len(code) + 1)
    for i, char in enumerate(code):
        char_img = Image.new("RGBA", (char_width + 6, height), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_img)
        color = tuple(random.randint(20, 110) for _ in range(3))
        char_draw.text((4, random.randint(2, 8)), char, font=font, fill=color)
        char_img = char_img.rotate(random.randint(-25, 25), resample=Image.BICUBIC)
        image.paste(char_img, (6 + i * char_width, 0), char_img)

    image = image.filter(ImageFilter.SMOOTH)

    from io import BytesIO
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
