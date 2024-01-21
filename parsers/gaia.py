import os
from pathlib import Path

import parsers.gen3


BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / ".."

DATA_DIR = BASE_DIR / "assets" / "data"

base_location = 0x4619C

mon_file = DATA_DIR / "pokemon.txt"
move_file = DATA_DIR / "moves.txt"
movepp_file = DATA_DIR / "movepps.txt"
item_file = DATA_DIR / "items.txt"
growth_file = DATA_DIR / "growth.txt"
nature_file = DATA_DIR / "natures.txt"
gender_file = DATA_DIR / "genders.txt"
growth_exp_file = DATA_DIR / "growth.json"

DEBUG = False
def p(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

with open(mon_file, "r", encoding="utf8") as f:
    MONLIST = f.read().splitlines()

with open(move_file, "r") as f:
    MOVELIST = f.read().splitlines()

with open(movepp_file, "r") as f:
    MOVEPPLIST = f.read().splitlines()
    MOVEPPLIST = [int(x) for x in MOVEPPLIST]

with open(item_file, "r") as f:
    ITEMLIST = f.read().splitlines()

with open(growth_file, "r") as f:
    growth = f.read().splitlines()
    GROWTH = {}
    for i in range(0, len(growth)):
        GROWTH[MONLIST[i]] = growth[i]

with open(nature_file, "r") as f:
    NATURES = f.read().splitlines()

with open(gender_file, "r") as f:
    GENDERS = f.read().splitlines()
    GENDERS = [int(x) for x in GENDERS]


Pokemon = parsers.gen3.make_parser(
    MONLIST,
    MOVELIST,
    MOVEPPLIST,
    ITEMLIST,
    GROWTH,
    NATURES,
    GENDERS,
)