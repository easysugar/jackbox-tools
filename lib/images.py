from typing import List

from PIL import Image, ImageDraw, ImageFont

from math import sqrt, ceil


def create_image(strokes: List[dict | str], background_color='white', color='#fe6100', thickness=16, size: int = None, padding: int = 16):
    strokes = [
        stroke if isinstance(stroke, dict) else {'points': stroke, 'color': color, 'thickness': thickness}
        for stroke in strokes
    ]
    # First pass: find canvas size
    max_x, max_y = 0, 0
    for stroke in strokes:
        if isinstance(stroke['points'], list):
            for p in stroke['points']:
                x, y = int(p['x']), int(p['y'])
                max_x = max(max_x, x)
                max_y = max(max_y, y)
        else:
            pts = stroke["points"].split("|")
            for p in pts:
                x, y = map(int, p.split(","))
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    max_x, max_y = max_x + 2*padding, max_y + 2*padding
    if size:
        max_x, max_y = size, size

    # Create image (add padding)
    img = Image.new("RGB", (max_x, max_y), background_color)
    draw = ImageDraw.Draw(img)

    # Draw strokes
    for stroke in strokes:
        thickness = stroke["thickness"]
        color = stroke["color"]

        if isinstance(stroke['points'], list):
            pts = [(int(p['x']), int(p['y'])) for p in stroke["points"]]
        else:
            pts = [tuple(map(int, p.split(","))) for p in stroke["points"].split("|")]

        # Draw connected lines
        if len(pts) > 1:
            draw.line(pts, fill=color, width=thickness)
        else:
            x, y = pts[0]
            draw.ellipse((x, y, x + thickness, y + thickness), fill=color)
    return img


def add_title(image, title, font_path="./fonts/a_AlbionicTitulInfl_Bold.ttf", font_size=26, padding=40):
    width, height = image.size
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # Measure text size
    dummy_img = Image.new("RGB", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)
    text_bbox = dummy_draw.textbbox((0, 0), title, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Create new image with extra space on top
    new_height = height + text_height + padding * 2
    new_img = Image.new("RGB", (width, new_height), "white")

    draw = ImageDraw.Draw(new_img)

    # Center text horizontally
    text_x = (width - text_width) // 2
    text_y = padding

    draw.text((text_x, text_y), title, fill="black", font=font)

    # Paste original image below title
    new_img.paste(image, (0, text_height + padding * 2))

    return new_img


def make_collage(images: List[Image.Image], cols: int = None, background_color='white') -> Image.Image:
    cols = cols or ceil(sqrt(cols))

    # Grab maximum width and height
    w, h = map(max, zip(*map(lambda img: img.size, images)))

    rows = (len(images) + cols - 1) // cols

    collage = Image.new("RGB", (cols * w, rows * h), background_color)

    for i, img in enumerate(images):
        row = i // cols
        col = i % cols

        x = col * w
        y = row * h

        collage.paste(img, (x, y))

    return collage
