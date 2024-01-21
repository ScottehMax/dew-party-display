import os
import re
from math import ceil, floor
from pathlib import Path

import PIL.Image
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import parsers.gaia
import parsers.gen3

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / ".."

monimage_folder = BASE_DIR / "assets" / "pokemon" / "crystal"
backup_monimage_folder = BASE_DIR / "assets" / "pokemon" / "pokeemerald-expansion"
# item_folder = BASE_DIR / "assets" / "items"
template_folder = BASE_DIR / "assets" / "template" / "gen2"
fonts_folder = BASE_DIR / "assets" / "fonts"

template = Image.open(template_folder / "partymember.png")
shiny = Image.open(template_folder / "shiny.png")
m_img = Image.open(template_folder / "male.png")
f_img = Image.open(template_folder / "female.png")
font = ImageFont.truetype(str(fonts_folder / 'gen1.ttf'), 9)


hpg = (88, 144, 96)
hpy = (192, 136, 40)
hpr = (184, 80, 72)


def new_party_image(mon: parsers.gaia.Pokemon) -> PIL.Image.Image:
    new_img = template.copy()
    draw = ImageDraw.Draw(new_img)
    draw.fontmode = "1"

    # draw the name
    # mon.nickname = "CYNDAQUIL"
    draw.text((64, 17), mon.nickname, (0, 0, 0), font=font)

    # draw level
    # mon.level = 5
    draw.text((120, 1), str(mon.level), (0, 0, 0), font=font)

    # draw species number
    draw.text((80, 1), f"{mon.species_no}", (0, 0, 0), font=font)

    # draw gender and shininess
    if mon.gender == "Male":
        new_img.alpha_composite(m_img, (144, 0))
    elif mon.gender == "Female":
        new_img.alpha_composite(f_img, (144, 0))

    if mon.shiny:
        new_img.alpha_composite(shiny, (152, 0))

    # draw HP text
    hp_text = f"{mon.current_hp}".rjust(3) + " " + f"{mon.max_hp}".rjust(3)
    draw.text((94, 39), hp_text, (0, 0, 0), font=font)
    # draw slash
    draw.text((118, 38), "/", (0, 0, 0), font=font)

    # draw status
    if not mon.status:
        mon.status = " OK"

    draw.text((32, 89), mon.status, (0, 0, 0), font=font)

    # draw item text
    if mon.item:
        item_text = mon.item
    else:
        item_text = "NONE"

    draw.text((64, 65), item_text, (0, 0, 0), font=font)

    # draw moves
    # mon.moves = ["TACKLE", "LEER", None, None]
    for i in range(len(mon.moves)):
        if mon.moves[i] is not None:
            draw.text((64, 81 + (16 * i)), mon.moves[i], (0, 0, 0), font=font)
        else:
            draw.text((64, 81 + (16 * i)), "-", (0, 0, 0), font=font)

    # draw PP
    for i in range(len(mon.pp)):
        if mon.moves[i] is not None:
            pp_text = f"{mon.pp[i]}".rjust(2) + "/" + f"{mon.max_pp[i]}".rjust(2)
            draw.text((120, 89 + (16 * i)), pp_text, (0, 0, 0), font=font)
        else:
            # blank out the pp area
            topleft = (96, 89 + (16 * i))
            bottomright = (111, min(96 + (16 * i), 142))
            draw.rectangle((topleft, bottomright), fill=(176, 216, 136))

            # draw the placeholder for pp text
            draw.text((96, 89 + (16 * i)), "--", (0, 0, 0), font=font)

    # draw HP bar
    hp_percent = mon.current_hp / mon.max_hp
    hp_width = ceil(47 * hp_percent)

    if hp_percent > 0.5:
        color = hpg
    elif hp_percent > 0.2:
        color = hpy
    else:
        color = hpr

    draw.rectangle((102, 33, 102 + hp_width, 34), fill=color)

    # draw EXP bar
    etl = parsers.gen3.experience_this_level(mon.experience, mon.growth)
    width = ceil(etl[0] / etl[1] * 64)
    print(width)

    offset = 150 - width

    if width > 0:
        draw.rectangle((offset, 49, 150, 50), fill=(56, 152, 216))
    
    # draw the sprite
    if mon.shiny:
        mon_fn = os.path.join(monimage_folder, f"{mon.species.lower()}-shiny.png")
    else:
        mon_fn = os.path.join(monimage_folder, f"{mon.species.lower()}.png")
    try:
        mon_img = Image.open(mon_fn)
    except:
        mon_fn = os.path.join(backup_monimage_folder, f"{mon.species.lower()}.png")
        mon_img = Image.open(mon_fn)

    # flip the mon image horizontally
    mon_img = mon_img.transpose(Image.FLIP_LEFT_RIGHT)

    new_img.alpha_composite(mon_img, (0, 0))

    return new_img


def create_image_3x2(results):
    width = 160
    height = 144

    img = Image.new('RGB', (width * 3, height * 2), (255, 255, 255))
    for i, mon in enumerate(results):
        new_img = new_party_image(mon)
        img.paste(new_img, (width * (i % 3), height * (i // 3)))

    return img