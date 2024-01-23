import os
from pathlib import Path

import parsers.gen1


base_location = 0x557A


BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / ".."
DATA_DIR = BASE_DIR / "assets" / "data" / "kep"

mon_id_file = DATA_DIR / "monids.txt"
names_file = DATA_DIR / "names.txt"
moves_file = DATA_DIR / "moves.txt"
movepps_file = DATA_DIR / "movepps.txt"
growth_file = DATA_DIR / "growth.txt"


with open(mon_id_file, "r") as f:
    MON_IDS = f.read().splitlines()

with open(names_file, "r") as f:
    NAMES = f.read().splitlines()

with open(moves_file, "r") as f:
    MOVES = f.read().splitlines()

with open(movepps_file, "r") as f:
    MOVE_PPS = f.read().splitlines()

with open(growth_file, "r") as f:
    GROWTH = f.read().splitlines()


Pokemon = parsers.gen1.make_parser(
    MON_IDS,
    NAMES,
    MOVES,
    MOVE_PPS,
    GROWTH,
)