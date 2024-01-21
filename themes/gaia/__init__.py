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
item_folder = BASE_DIR / "assets" / "items"
template_folder = BASE_DIR / "assets" / "template" / "gaia"
fonts_folder = BASE_DIR / "assets" / "fonts"


def set_sprite_folder(sprites_folder: str):
    global sprites
    global monimage_folder
    sprites = sprites_folder
    monimage_folder = BASE_DIR / "assets" / "pokemon" / sprites


def draw_with_shadow(x, y, draw, text, font, color, shadow_color, anchor="la"):
    draw.text((x+1, y), text, shadow_color, font=font, anchor=anchor)
    draw.text((x, y+1), text, shadow_color, font=font, anchor=anchor)
    draw.text((x+1, y+1), text, shadow_color, font=font, anchor=anchor)
    draw.text((x, y), text, color, font=font, anchor=anchor)


template = Image.open(template_folder / "partymember.png")
expfull = Image.open(template_folder / "expfull.png")
expempty = Image.open(template_folder / "expempty.png")
fl = ImageFont.truetype(str(fonts_folder / 'pkmnfl.ttf'), 12)
ems = ImageFont.truetype(str(fonts_folder / 'pkmnems.ttf'), 11)
hpghl = (24, 214, 33)
hpgsh = (0, 165, 0)
hpyhl = (255, 222, 0)
hpysh = (239, 173, 8)
hprhl = (255, 90, 41)
hprsh = (173, 49, 57)
hpbghl = (255, 255, 222)
hpbgsh = (206, 181, 123)
# shadow_color = (167, 156, 14)
shadow_color = (133, 164, 184)



def normalize_item_name(name: str) -> str:
    # replace spaces with _, remove all non-A-Za-z
    name = name.replace(" ", "_").replace('-', '_')
    name = re.sub(r"[^A-Za-z_]", "", name)
    return name.lower()


def new_party_image(mon: PokemonProtocol) -> PIL.Image.Image:
    new_img = template.copy()
    draw = ImageDraw.Draw(new_img)

    # draw the name
    if mon.egg:
        draw_with_shadow(10, 10, draw, f"Egg", fl, (0, 0, 0), shadow_color)
        draw.text((155, 50), f"Cycles left: {mon.friendship}\n (~{mon.friendship*256} steps)", (0, 0, 0), font=ems, anchor="ma")
    else:
        draw_with_shadow(10, 10, draw, f"{mon.nickname}", fl, (0, 0, 0), shadow_color)
    # draw aligned to right
    draw_with_shadow(190, 10, draw, f"Lv{mon.level}", fl, (0, 0, 0), shadow_color, "ra")

    # draw the sprite
    if mon.shiny:
        mon_fn = os.path.join(monimage_folder, f"{mon.species.lower()}_shiny.png")
    else:
        mon_fn = os.path.join(monimage_folder, f"{mon.species.lower()}.png")
    try:
        mon_img = Image.open(mon_fn)
    except:
        mon_fn = os.path.join(backup_monimage_folder, f"{mon.species.lower()}.png")
        mon_img = Image.open(mon_fn)
    new_img.alpha_composite(mon_img, (68, 29))

    # draw item sprite
    if mon.item:
        item_fn = os.path.join(item_folder, f"{normalize_item_name(mon.item)}.png")
        item_img = Image.open(item_fn)
        new_img.alpha_composite(item_img, (146, 40))
        draw.text((159, 63), f"{mon.item}", (0, 0, 0), font=ems, anchor="ma")

    # add status
    if mon.status:
        img = Image.open(template_folder / f"{mon.status.lower()}.png")
        new_img.alpha_composite(img, (90, 11))

    # draw hp bar. first, draw the bg
    draw.rectangle((83, 97, 83 + 47, 97 + 1), fill=hpbghl)
    draw.rectangle((83, 96, 83 + 47, 96), fill=hpbgsh)

    # then, draw the filled part of the bar
    width = ceil(mon.current_hp / mon.max_hp * 47)
    # handle color
    if mon.current_hp / mon.max_hp > 0.5:
        hlcolor = hpghl
        shcolor = hpgsh
    elif mon.current_hp / mon.max_hp > 0.20:
        hlcolor = hpyhl
        shcolor = hpysh
    else:
        hlcolor = hprhl
        shcolor = hprsh

    if mon.current_hp > 0:
        draw.rectangle((83, 97, 83 + width, 97 + 1), fill=hlcolor)
        draw.rectangle((83, 96, 83 + width, 96), fill=shcolor)

    # draw the hp text
    draw.text((101, 104), f"{mon.current_hp}/{mon.max_hp}", (66, 66, 66), font=fl, anchor="ma")

    # deal with exp
    etl = parsers.gen3.experience_this_level(mon.experience, mon.growth)
    # first, draw the bg
    new_img.paste(expempty, (74, 121), expempty)

    # then, draw the bar
    width = ceil(etl[0] / etl[1] * 64)
    # crop full bar to width
    expfull_cropped = expfull.crop((0, 0, width, 3))
    new_img.paste(expfull_cropped, (74, 121), expfull_cropped)

    # draw the exp text

    draw.text((101, 127), f"To next level: {etl[1] - etl[0]}", (66, 66, 66), font=ems, anchor="ma")

    # moves
    for i in range(len(mon.moves)):
        if mon.moves[i] is not None:
            draw.text((44, 148 + i*14), f"{mon.moves[i]}", (0, 0, 0), font=fl, anchor="la")
        else:
            # draw white rectangle
            draw.rectangle((44, 148 + i*14, 44 + 80, 148 + i*14 + 12), fill=(255, 255, 255))

    # pp
    for i in range(len(mon.pp)):
        if mon.moves[i] is not None:
            draw.text((128, 148 + i*14), f"{mon.pp[i]}/{mon.max_pp[i]}", (0, 0, 0), font=fl, anchor="la")
        else:
            # draw white rectangle
            draw.rectangle((108, 148 + i*14, 128 + 20, 148 + i*14 + 12), fill=(255, 255, 255))

    return new_img


def create_image_6x1(results):
    width = 1200
    height = 212

    img = Image.new('RGB', (width, height), color = 'white')
    for i, mon in enumerate(results):
        new_img = new_party_image(mon)
        img.paste(new_img, (i*200, 0))

    return img


def create_image_3x2(results):
    width = 600
    height = 424

    img = Image.new('RGB', (width, height), color = 'white')
    for i, mon in enumerate(results):
        new_img = new_party_image(mon)
        img.paste(new_img, (i%3*200, i//3*212))

    return img
