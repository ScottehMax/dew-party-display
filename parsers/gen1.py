import struct
from typing import Optional, Type

from parsers import Gen1Protocol


def get_status(status_byte) -> Optional[str]:
    if status_byte & 0x04:
        return "SLP"
    elif status_byte & 0x08:
        return "PSN"
    elif status_byte & 0x10:
        return "BRN"
    elif status_byte & 0x20:
        return "FRZ"
    elif status_byte & 0x40:
        return "PAR"
    return None


def level_to_experience_f(level: int, growth: str) -> int:
    if growth == "Fast":
        return int(4 * (level ** 3) / 5)
    elif growth == "Medium Fast":
        return level ** 3
    elif growth == "Medium Slow":
        return int((6 / 5) * (level ** 3) - 15 * (level ** 2) + 100 * level - 140)
    elif growth == "Slow":
        return int(5 * (level ** 3) / 4)
    elif growth == "Slightly Fast":
        return int((3 * (level ** 3))/4 + (10 * (level ** 2)) - 30)
    elif growth == "Slightly Slow":
        return int((3 * (level ** 3))/4 + (20 * (level ** 2)) - 70)

    return 0


EXP_TABLE = {}

GROWTH_TYPES = [
    "Fast",
    "Medium Fast",
    "Medium Slow",
    "Slow",
    "Slightly Fast",
    "Slightly Slow"
]

for g in GROWTH_TYPES:
    EXP_TABLE[g] = [level_to_experience_f(level, g) for level in range(1, 101)]


def level_to_experience(level: int, growth: str) -> int:
    return EXP_TABLE[growth][level - 1]


def experience_to_level(experience: int, growth: str) -> int:
    for i in range(100):
        if EXP_TABLE[growth][i] > experience:
            return i
    return 100


def experience_this_level(exp: int, growth: Optional[str]) -> tuple[int, int]:
    if growth is None:
        return 0, 0
    for i in range(100):
        if EXP_TABLE[growth][i] > exp:
            # current exp, next level exp (relative)
            return exp - EXP_TABLE[growth][i - 1], EXP_TABLE[growth][i] - EXP_TABLE[growth][i - 1]
    return 0, 0


chars = [ "",  "",  "",  "",  "",  "",  "",  "",  "",  "",  "",  "",  "",  "",  "",  " ", 
  "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P",
  "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "(", ")", ":", ";", "[", "]",
  "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
  "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "é","'d","'l","'s","'t","'v",
  " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ",
  " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ",
  "'", "ᴾᴋ","ᴹɴ","-","'r","'m", "?", "!", ".", "ァ", "ゥ", "ェ", "▷", "▶", "▼",	 "♂",
  "$", "×", ".", "/", ",", "♀", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" ]


def decode_nickname(nick_bytes):
    # remove everything from 0x50 onwards
    if 0x50 in nick_bytes:
        nick_bytes = nick_bytes[:nick_bytes.index(0x50)]
    # decode the nickname
    res = "".join([chars[b-0x70] for b in nick_bytes])
    return res


def make_parser(
    MONIDS,
    MONNAMES,
    MOVES,
    MOVEPPS,
    GROWTH
) -> Type[Gen1Protocol]:
    class Gen1Mon:
        def __init__(self, data: bytes):
            # 44 bytes + 10 nickname bytes
            species = data[0]

            self.species = MONNAMES[species]
            self.species_no = species
            self.growth = GROWTH[species]

            self.sprite = MONIDS[species]

            self.current_hp = struct.unpack(">H", data[1:3])[0]
            self.status = get_status(data[4])
            moves = data[8:12]
            self.moves = []
            for move in moves:
                if move > 0:
                    self.moves.append(MOVES[move - 1])
                else:
                    self.moves.append(None)
            self.level = data[33]
            self.max_hp = struct.unpack(">H", data[34:36])[0]
            pp = list(struct.unpack("<BBBB", data[29:33]))
            self.pp = []
            for i in range(0, 4):
                self.pp.append(pp[i] if self.moves[i] else None)


            self.max_pp = []
            for move in moves:
                if move > 0:
                    self.max_pp.append(int(MOVEPPS[move - 1]))
                else:
                    self.max_pp.append(None)

            self.nickname = decode_nickname(data[44:54])
            print(self.nickname, self.species)

            self.shiny = False
            self.egg = False
            self.item = False
            self.gender = "Genderless"
            
            self.experience = int.from_bytes(data[14:17], "big")
            print(self.experience, data[14:17])



    return Gen1Mon