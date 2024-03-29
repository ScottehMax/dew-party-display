import os
import re
from math import ceil
from pathlib import Path

import PIL.Image
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import parsers.gaia
import parsers.gen3
from parsers import PokemonProtocol


BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / ".."

sprites = "pokeemerald-expansion"
monimage_folder = BASE_DIR / "assets" / "pokemon" / sprites
backup_monimage_folder = BASE_DIR / "assets" / "pokemon" / "pokeemerald-expansion"
# item_folder = BASE_DIR / "assets" / "items"
template_folder = BASE_DIR / "assets" / "template" / "gen1"
fonts_folder = BASE_DIR / "assets" / "fonts"


def set_sprite_folder(sprites_folder: str):
    global sprites
    global monimage_folder
    sprites = sprites_folder
    monimage_folder = BASE_DIR / "assets" / "pokemon" / sprites


template = Image.open(template_folder / "partymember.png")
font = ImageFont.truetype(str(fonts_folder / 'gen1.ttf'), 9)


hpg = (88, 144, 96)
hpy = (192, 136, 40)
hpr = (184, 80, 72)


def new_party_image(mon: PokemonProtocol) -> PIL.Image.Image:
    new_img = template.copy()
    draw = ImageDraw.Draw(new_img)
    draw.fontmode = "1"

    # draw the name
    draw.text((72, 9), mon.nickname, (0, 0, 0), font=font)

    # draw level
    draw.text((120, 17), str(mon.level), (0, 0, 0), font=font)

    # draw HP text
    hp_text = f"{mon.current_hp}".rjust(3) + "/" + f"{mon.max_hp}".rjust(3)
    draw.text((96, 33), hp_text, (0, 0, 0), font=font)

    # draw status
    if not mon.status:
        mon.status = "OK"

    draw.text((128, 49), mon.status, (0, 0, 0), font=font)

    # draw moves
    for i in range(len(mon.moves)):
        move = mon.moves[i]
        if move is not None:
            draw.text((16, 73 + (16 * i)), move, (0, 0, 0), font=font)
        else:
            draw.text((16, 73 + (16 * i)), "-", (0, 0, 0), font=font)

    # draw PP
    for i in range(len(mon.pp)):
        if mon.moves[i] is not None:
            pp_text = f"{mon.pp[i]}".rjust(2) + "/" + f"{mon.max_pp[i]}".rjust(2)
            draw.text((112, 81 + (16 * i)), pp_text, (0, 0, 0), font=font)
        else:
            # blank out the pp area
            topleft = (88, 81 + (16 * i))
            bottomright = (103, 88 + (16 * i))
            draw.rectangle((topleft, bottomright), fill=(255, 255, 255))

            # draw the placeholder for pp text
            draw.text((88, 81 + (16 * i)), "--", (0, 0, 0), font=font)

    # draw HP bar
    hp_percent = mon.current_hp / mon.max_hp
    hp_width = ceil(47 * hp_percent)

    if hp_percent > 0.5:
        color = hpg
    elif hp_percent > 0.2:
        color = hpy
    else:
        color = hpr

    draw.rectangle((104, 27, 104 + hp_width, 28), fill=color)

    # draw the sprite
    if mon.shiny:
        mon_fn = os.path.join(monimage_folder, f"{mon.species.lower()}-shiny.png")
        if not os.path.exists(mon_fn):
            mon_fn = os.path.join(monimage_folder, f"{mon.species.lower()}.png")
    else:
        mon_fn = os.path.join(monimage_folder, f"{mon.species.lower()}.png")

    try:
        mon_img = Image.open(mon_fn)
    except:
        mon_fn = os.path.join(backup_monimage_folder, f"{mon.species.lower()}.png")
        mon_img = Image.open(mon_fn)

    mon_img = mon_img.transpose(Image.FLIP_LEFT_RIGHT)

    new_img.alpha_composite(mon_img, (0, 0))

    return new_img


def create_image_6x1(results):
    width = 160
    height = 144

    img = Image.new('RGB', (width * 6, height), (255, 255, 255))
    for i, mon in enumerate(results):
        new_img = new_party_image(mon)
        img.paste(new_img, (width * i, 0))

    return img


def create_image_3x2(results):
    width = 160
    height = 144

    img = Image.new('RGB', (width * 3, height * 2), (255, 255, 255))
    for i, mon in enumerate(results):
        new_img = new_party_image(mon)
        img.paste(new_img, (width * (i % 3), height * (i // 3)))

    return img
