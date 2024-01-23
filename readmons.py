import configparser
import os
import sys
from math import ceil
from pathlib import Path
from typing import cast

# import parsers.gaia
import parsers.kep
from themes import Theme


current_directory = Path(os.path.dirname(os.path.abspath(__file__)))


if len(sys.argv) > 1:
    state_id = sys.argv[1]
else:
    state_id = None


config = configparser.ConfigParser()
config.read(current_directory / "config.ini")
folder = Path(config["general"]["dew_folder"])
output_fn = folder / config["general"]["output_filename"]
web_fn = folder / config["general"]["web_filename"]
use_web = config["general"].getboolean("use_web")
theme_name = config["general"]["theme"]
sprites = config["general"]["sprites"]


# import the theme from themes
import importlib
try:
    theme = cast(Theme, importlib.import_module("." + theme_name, "themes"))
    theme.set_sprite_folder(sprites)
except ModuleNotFoundError:
    print(f"Theme {theme_name} not found.")
    sys.exit(1)

if state_id is None:
    state_id_file = folder / "state"

    with open(state_id_file, "r") as f:
        state_id = f.read().splitlines()[0]

save_folder = folder / config["general"]["save_folder"]
state_file = save_folder / f"save_{state_id}.state"


def save_image_6x1(results):
    img = theme.create_image_6x1(results)
    img.save(output_fn)

    if use_web:
        img.save(web_fn)


def create_image_3x2(results):
    img = theme.create_image_3x2(results)
    img.save(output_fn)
    if use_web:
        img.save(web_fn)


def main():
    results = []

    with open(state_file, "rb") as f:
        for i in range(6):
            # f.seek(parsers.gaia.base_location + i*100)
            # monb = f.read(100)
            f.seek(parsers.kep.base_location + i*44)
            monb = f.read(44)
            f.seek(parsers.kep.base_location + 0x14a + i*11)
            nicknameb = f.read(10)
            print(nicknameb)
            mon = parsers.kep.Pokemon(monb + nicknameb)
            if mon.species_no != 0:
                results.append(mon)

    create_image_3x2(results)


if __name__ == "__main__":
    main()
