from collections import defaultdict
from io import BytesIO
from typing import Union

import requests
import tqdm
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
from pilmoji import Pilmoji

# from IPython.display import display
from settings.report import *

progressbar_color = GREY
translate_color = BLUE
approve_color = GREEN


def load_img_from_url(url):
    if url.startswith('http'):
        response = requests.get(url)
        return Image.open(BytesIO(response.content))
    return Image.open(open(url, 'rb'))


def center_image(img, ratio=1.0):
    width, height = img.size  # Get dimensions
    new_width = min(width, height)
    new_height = new_width * ratio
    left = (width - new_width) / 2
    top = (height - new_height) / 2
    right = (width + new_width) / 2
    bottom = (height + new_height) / 2
    return img.crop((left, top, right, bottom))


# def crop_to_circle(img: Image):
#     npImage = np.array(img)
#     h, w = img.size
#     # Create same size alpha layer with circle
#     alpha = Image.new('L', img.size, 'black')
#     draw = ImageDraw.Draw(alpha)
#     #     draw.pieslice([0,0,h,w],0,360,fill=255)
#     draw.pieslice(((0, 0), (h, w)), 0, 360, fill=256)
#
#     # Convert alpha Image to numpy array
#     npAlpha = np.array(alpha)
#
#     if npImage.shape[-1] == 4:
#         # replace alpha layer
#         npImage[:, :, -1] = npAlpha
#     else:
#         # add alpha layer to RGB
#         npImage = np.dstack((npImage, npAlpha))
#     return Image.fromarray(npImage)

def crop_to_circle(img: Image):
    img = img.convert('RGBA')
    bigsize = (img.size[0] * 3, img.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(img.size, Image.LANCZOS)
    mask = ImageChops.darker(mask, img.split()[-1])
    img.putalpha(mask)
    return img
    # bigsize = (img.size[0] * 3, img.size[1] * 3)
    # mask = Image.new('L', bigsize, 0)
    # draw = ImageDraw.Draw(mask)
    # draw.ellipse((0, 0) + bigsize, fill=255)
    # mask = mask.resize(img.size, Image.ANTIALIAS)
    # img.putalpha(mask)
    # return img


def draw_text(img: Image, font: ImageFont, text: str, width, height, margin_up: Union[float, int] = 0, margin_left: Union[float, int] = 0,
              fill="white", drawer=None, align='center', icon: str = None, icon_size: int = None):
    if font is None:
        font = ImageFont.load_default()

    if drawer is None:
        d = ImageDraw.Draw(img)
        w, h = get_text_size(d, font, text)
    else:
        d = drawer
        w, h = get_text_size(drawer, font, text)

    if isinstance(margin_up, float):
        margin_up = int(margin_up * height)

    if isinstance(margin_left, float):
        margin_left = int(margin_left * width)

    if align == 'center':
        x, y = (width - w) // 2 + margin_left, margin_up + (height - h) // 2
    elif align == 'top':
        x, y = (width - w) // 2 + margin_left, margin_up
    elif align == 'left bottom':
        x, y = margin_left, height - h + margin_up
    elif align == 'right bottom':
        x, y = width - w + margin_left, height - h + margin_up
    elif align == 'right':
        x, y = width - w + margin_left, margin_up
    else:
        x, y = margin_left, margin_up

    if icon:
        icon_size = icon_size or h
        icon = load_img_from_url(icon).resize((icon_size, icon_size))
        icon = crop_to_circle(icon)
        img.paste(icon, (x, y), icon)
        x += int(icon.width * 1.5)

    d.text((x, y), text, font=font, fill=fill)


def draw_game_title(img: Image, game: str, width: int, height: int):
    if 'name' not in GAMES[game]:
        return
    text = GAMES[game]['name']
    width, height = width, height * 3 // 4
    f = ImageFont.truetype(*FONT_GAME)
    draw_text(img, f, text, width, height)


def draw_game_percent(img: Image, game: str, width: int, height: int):
    try:
        p = PROGRESS[game]
    except KeyError:
        return
    tr, apr = p['translated'], p['approved']
    if not tr:
        return
    new_bar(img, width // 5, height * 2 // 3, width * 3 // 5, 15, tr / 100, apr / 100)

    font = ImageFont.truetype(*FONT_PERCENT)

    text = '%d%%📝 %d%%✅' % (tr, apr)
    draw_text(img, font, text, width, height, drawer=Pilmoji(img), margin_up=0.1)


def draw_text_vertically(img: Image, text: str, x: int, y: int, width: int, height: int):
    f = ImageFont.truetype(*FONT_HEAD)
    txt = Image.new('L', (width, height))

    d = ImageDraw.Draw(txt)
    w, h = get_text_size(d, f, text)
    d.text(((width - w) / 2, (height - h) / 2), text, font=f, fill="white")
    # d.text((0, 0), text, font=f, fill=255)
    w = txt.rotate(90, expand=True)
    # img.paste(ImageOps.colorize(w, (0, 0, 0), (255, 255, 84)), (x, y), w)
    img.paste(w, (x, y))


def get_text_size(draw, font, text):
    ascent, descent = font.getmetrics()
    try:
        w = max(draw.textlength(t, font=font) for t in text.split('\n'))
        try:
            h = sum(font.getmask(t).getbbox()[3] + descent for t in text.split('\n'))
        except:
            h = font.size
    except:
        w, h = draw.getsize(text, font=font)
    return w, h


def draw_voice_actor(img: Image, game: str, width: int, height: int):
    actor: dict = GAMES[game].get('actor')
    if not actor:
        return
    font = ImageFont.truetype(*FONT_VOICE)
    # text = f'🔊 {actor}'
    text = actor['name']
    draw_text(img, font, text, width, height, drawer=Pilmoji(img), margin_up=-0.05, margin_left=0.05, align='left bottom',
              icon=actor['img'])


def draw_status_icon(img: Image, game: str, width: int, height: int):
    status = GAMES[game].get('status')
    if not status:
        return
    font = ImageFont.truetype(*FONT_VOICE)
    draw_text(img, font, status, width, height, drawer=Pilmoji(img), margin_up=-0.05, margin_left=-0.05, align='right bottom')


def draw_top_contributors(img: Image, width: int, height: int, margin_up: int):
    font = ImageFont.truetype(*FONT_CONTRIBUTORS)
    # font = None
    for i, user in enumerate(CONTRIBUTORS, 1):
        draw_text(img, font, user['username'], width, height, margin_left=0.1, margin_up=margin_up + int(ROW_CONTRIBUTORS * i * height),
                  align='none', icon=user['avatarUrl'], icon_size=FONT_CONTRIBUTORS[1])
        draw_text(img, font, str(user['count']), width, height, margin_left=-0.05, margin_up=margin_up + int(ROW_CONTRIBUTORS * i * height),
                  align='right', fill=BLUE)


def draw_top_patrons(img: Image, width: int, height: int, margin_up: int):
    font = ImageFont.truetype(*FONT_CONTRIBUTORS)
    for i, user in enumerate(PATRONS, 1):
        draw_text(img, font, user['name'], width, height, margin_left=0.1, margin_up=margin_up + int(ROW_CONTRIBUTORS * i * height),
                  align='none', icon=user['url'], icon_size=FONT_CONTRIBUTORS[1])


def create_game_icon(game: str, width: int, height: int):
    url = GAMES[game]['img']
    img = load_img_from_url(url)
    filtered = img.filter(ImageFilter.GaussianBlur(radius=5))
    #     filtered.putalpha(128)
    #     filtered = Image.eval(filtered, lambda x: x*0.5)
    #         .filter(ImageFilter.BLUR)
    #         .filter(ImageFilter.SMOOTH_MORE),
    bg = center_image(filtered, ratio=height / width)
    bg = bg.resize((width, height))
    fg = img.resize((width, img.size[1] * width // img.size[0]))
    bg.paste(fg, (0, bg.size[1] // 2 - fg.size[1] // 2))

    enhancer = ImageEnhance.Brightness(bg)
    img = enhancer.enhance(0.5)
    draw_game_title(img, game, width, height)
    draw_game_percent(img, game, width, height)
    draw_voice_actor(img, game, width, height)
    draw_status_icon(img, game, width, height)
    return img


def create_logo(width, height):
    bg = Image.new("RGBA", (width, height), 'black')
    img = load_img_from_url(LOGO_IMAGE)
    scale = min(width / img.width, height / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)))
    bg.paste(img, (bg.size[0] // 2 - img.size[0] // 2, bg.size[1] // 2 - img.size[1] // 2), img)
    f = ImageFont.truetype(*FONT_HEAD)
    draw_text(bg, f, LOGO_TEXT, width, height, align='right bottom', margin_up=-height // 10, margin_left=-width // 10, fill='yellow')
    return bg


def create_top_contributors_icon(width: int, height: int):
    img = Image.new("RGBA", (width, height), 'black')
    font = ImageFont.truetype(*FONT_HEAD)
    draw_text(img, font, TOP_CONTRIBUTORS_TEXT, width, height, align='top', margin_up=0.1, fill='yellow')
    draw_top_contributors(img, width, height, int(0.1 * height))
    return img


def create_top_patrons_icon(width: int, height: int):
    img = Image.new("RGBA", (width, height), 'black')
    font = ImageFont.truetype(*FONT_HEAD)
    draw_text(img, font, TOP_PATRONS_TEXT, width, height, align='top', margin_up=0.1, fill='yellow')
    draw_top_patrons(img, width, height, int(0.1 * height))
    return img


def create_games_grid(grid, width, height, max_cnt=2, head_margin=50) -> Image:
    n, m = head_margin + max_cnt * width, len(grid) * height
    canvas = Image.new("RGBA", (n, m), 'black')
    for i, (name, row) in tqdm.tqdm(list(enumerate(grid.items()))):
        draw_text_vertically(canvas, name, 0, i * height, height, head_margin)
        for j, game in enumerate(row):
            img = create_game_icon(game, width, height)
            x, y = head_margin + j * width, i * height
            canvas.paste(img, (x, y))
    if CONTRIBUTORS:
        img = create_top_contributors_icon(width, height * 2)
        i, j = CONTRIBUTORS_POSITION
        x, y = head_margin + j * width, i * height
        canvas.paste(img, (x, y))
    if PATRONS:
        img = create_top_patrons_icon(width, height * 2)
        i, j = PATRONS_POSITION
        x, y = head_margin + j * width, i * height
        canvas.paste(img, (x, y))
    if LOGO_IMAGE:
        img = create_logo(width, height)
        i, j = LOGO_POSITION
        x, y = head_margin + j * width, i * height
        canvas.paste(img, (x, y))
    return canvas


def new_bar(img, x, y, width, height, translate_progress, approve_progress,
            fg=translate_color, fg2=approve_color, bg=progressbar_color):
    draw = ImageDraw.Draw(img)

    draw.rectangle((x + (height / 2), y, x + width + (height / 2), y + height), fill=bg, width=10)
    draw.ellipse((x + width, y, x + height + width, y + height), fill=bg)
    draw.ellipse((x, y, x + height, y + height), fill=bg)

    # Draw the part of the progress bar that is actually filled
    w = int(width * translate_progress)
    draw.rectangle((x + (height / 2), y, x + w + (height / 2), y + height), fill=fg, width=10)
    draw.ellipse((x + w, y, x + height + w, y + height), fill=fg)
    draw.ellipse((x, y, x + height, y + height), fill=fg)

    # Draw the part of the progress bar that is actually filled x2
    w = int(width * approve_progress)
    draw.rectangle((x + (height / 2), y, x + w + (height / 2), y + height), fill=fg2, width=10)
    draw.ellipse((x + w, y, x + height + w, y + height), fill=fg2)
    draw.ellipse((x, y, x + height, y + height), fill=fg2)


def create_report():
    grid = defaultdict(list)
    for game in GAMES:
        grid[GAMES[game]['pack']].append(game)

    img = create_games_grid(grid, WIDTH, HEIGHT, COLUMNS_COUNT)
    img.save("report.png", "PNG")
    img.show()
