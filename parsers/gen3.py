import struct
from typing import Optional, Type

from parsers import PokemonProtocol


DEBUG = False
def p(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


ENCODING_TABLE = [
    # 0x00-0x0F
    " ", "À", "Á", "Â", "Ç", "È", "É", "Ê", "Ë", "Ì", " ", "Î", "Ï", "Ò", "Ó", "Ô",
    # 0x10-0x1F
    "Œ", "Ù", "Ú", "Û", "Ñ", "ß", "à", "á", "ね", "ç", "è", "é", "ê", "ë", "ì", " ",
    # 0x20-0x2F
    "î", "ï", "ò", "ó", "ô", "œ", "ù", "ú", "û", "ñ", "º", "ª", "ᵉʳ", "&", "+", " ",
    # 0x30-0x3F
    " ", " ", " ", " ", "Lv", "=", ";", " ", " ", " ", " ", " ", " ", " ", " ", " ",
    # 0x40-0x4F
    " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ",
    # 0x50-0x5F
    "▯", "¿", "¡", "PK", "MN", "PO", "Ké", "BL", "OC", "K", "Í", "%", "(", ")", " ", " ",
    # 0x60-0x6F
    " ", " ", " ", " ", " ", " ", " ", " ", "â", " ", " ", " ", " ", " ", " ", "í",
    # 0x70-0x7F
    " ", " ", " ", " ", " ", " ", " ", " ", " ", "⬆", "⬇", "⬅", "➡", " ", " ", " ",
    # 0x80-0x8F
    " ", " ", " ", " ", "ᵉ", "<", ">", " ", " ", " ", " ", " ", " ", " ", " ", " ",
    # 0x90-0x9F
    " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ",
    # 0xA0-0xAF
    "ʳᵉ", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "!", "?", ".", "-", "・",
    # 0xB0-0xBF
    "…", '“', "”", "‘", "’", "♂", "♀", "$", ",", "×", "/", "A", "B", "C", "D", "E",
    # 0xC0-0xCF
    "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
    # 0xD0-0xDF
    "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
    # 0xE0-0xEF
    "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "▶",
    # 0xF0-0xFF
    ":", "Ä", "Ö", "Ü", "ä", "ö", "ü", " ", " ", " ", " ", " ", " ", " ", " ", " ",
]


DATA_ORDERS = [
    "GAEM",
    "GAME",
    "GEAM",
    "GEMA",
    "GMAE",
    "GMEA",
    "AGEM",
    "AGME",
    "AEGM",
    "AEMG",
    "AMGE",
    "AMEG",
    "EGAM",
    "EGMA",
    "EAGM",
    "EAMG",
    "EMGA",
    "EMAG",
    "MGAE",
    "MGEA",
    "MAGE",
    "MAEG",
    "MEGA",
    "MEAG"
]


def decode(bytes: bytes) -> str:
    return "".join(ENCODING_TABLE[b] for b in bytes)


def get_status(status_byte) -> Optional[str]:
    if status_byte & 0b1 or status_byte & 0b10 or status_byte & 0b100:
        return "SLP"
    elif status_byte & 0b1000:
        return "PSN"
    elif status_byte & 0b10000:
        return "BRN"
    elif status_byte & 0b100000:
        return "FRZ"
    elif status_byte & 0b1000000:
        return "PAR"
    elif status_byte & 0b10000000:
        return "TOX"
    else:
        return None


def level_to_experience_f(level: int, growth: str) -> int:
    if growth == "Erratic":
        if level < 50:
            return int(((level ** 3) * (100 - level)) / 50)
        elif level < 68:
            return int(((level ** 3) * (150 - level)) / 100)
        elif level < 98:
            return int(((level ** 3) * int((1911 - (10 * level)) / 3)) / 500)
        elif level <= 100:
            return int(((level ** 3) * (160 - level)) / 100)
    elif growth == "Fast":
        return int(4 * (level ** 3) / 5)
    elif growth == "Medium Fast":
        return level ** 3
    elif growth == "Medium Slow":
        return int((6 / 5) * (level ** 3) - 15 * (level ** 2) + 100 * level - 140)
    elif growth == "Slow":
        return int(5 * (level ** 3) / 4)
    elif growth == "Fluctuating":
        if level < 15:
            return int((level ** 3) * ((int((level + 1) / 3) + 24) / 50))
        elif level < 36:
            return int((level ** 3) * ((level + 14) / 50))
        elif level <= 100:
            return int((level ** 3) * ((int(level / 2) + 32) / 50))

    return 0


EXP_TABLE = {}

GROWTH_TYPES = [
    "Erratic",
    "Fast",
    "Medium Fast",
    "Medium Slow",
    "Slow",
    "Fluctuating"
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



def calc_pp_bonus(pp: int, bonus: int) -> int:
    return int(pp + (pp * bonus / 5))


def make_parser(
    MONLIST,
    MOVELIST,
    MOVEPPLIST,
    ITEMLIST,
    GROWTH,
    NATURES,
    GENDERS,
) -> Type[PokemonProtocol]:
    class Pokemon:
        def __init__(self, data: bytes):
            # 100 bytes.

            # 0x00-0x03: Personality value
            self.pid = struct.unpack_from("<I", data, 0x00)[0]

            self.nature = NATURES[self.pid % 25]

            p("PID:", hex(self.pid))

            # 0x04-0x07: OTID
            self.otid = struct.unpack_from("<I", data, 0x04)[0]
            self.sid, self.id = self.otid >> 16, self.otid & 0xFFFF

            p("OTID:", hex(self.otid))
            p("ID:", self.id)
            p("SID:", self.sid)

            self.shiny = (self.pid >> 16) ^ (self.pid & 0xFFFF) ^ (self.otid >> 16) ^ (self.otid & 0xFFFF) < 8

            # 0x08-0x12: Nickname
            self.nickname = decode(data[0x08:0x12])
            # remove everything after the first 0xFF if it exists
            if 0xFF in data[0x08:0x12]:
                self.nickname = self.nickname[:data[0x08:0x12].index(b'\xFF')]

            p("Nickname:", self.nickname)

            # 0x12: Language
            self.language = data[0x12]

            p("Language:", self.language)

            # 0x13: Misc flags
            self.misc_flags = data[0x13]

            p("Misc flags:", hex(self.misc_flags))

            # 0x14-0x1A: OT name
            self.ot_name = decode(data[0x14:0x1A])
            # remove everything after the first 0xFF if it exists
            if 0xFF in data[0x14:0x1A]:
                self.ot_name = self.ot_name[:data[0x14:0x1A].index(b'\xFF')]

            p("OT name:", self.ot_name)

            # 0x1B: Markings
            self.markings = data[0x1B]

            # 0x1C-0x1D: Checksum
            self.checksum = struct.unpack_from("<H", data, 0x1C)[0]

            p("Checksum:", hex(self.checksum))

            # 0x1E-0x1F: Unused
            self.unused = data[0x1E:0x20]

            # 0x20-0x4F: Data
            self.data = data[0x20:0x50]
            self.decrypt_data()
            self.parse_substructure()

            gender_val = self.pid % 256
            species_gender = GENDERS[self.species_no - 1]

            if species_gender == 0:
                self.gender = "Male"
            elif species_gender == 254:
                self.gender = "Female"
            elif species_gender == 255:
                self.gender = "Genderless"
            else:
                if gender_val >= species_gender:
                    self.gender = "Male"
                else:
                    self.gender = "Female"

            self.growth = GROWTH[self.species] if self.species_no != 0 else None

            # 0x50: Status
            self.status = get_status(data[0x50])

            # 0x54: Level
            self.level = data[0x54]

            # 0x55: Mail ID
            self.mail_id = data[0x55]

            # 0x56-0x57: Current HP
            self.current_hp = struct.unpack_from("<H", data, 0x56)[0]
            if self.current_hp == 0:
                self.status = "FNT"

            # 0x58-0x59: Max HP
            self.max_hp = struct.unpack_from("<H", data, 0x58)[0]

            # 0x5A-0x5B: Attack
            self.attack = struct.unpack_from("<H", data, 0x5A)[0]

            # 0x5C-0x5D: Defense
            self.defense = struct.unpack_from("<H", data, 0x5C)[0]

            # 0x5E-0x5F: Speed
            self.speed = struct.unpack_from("<H", data, 0x5E)[0]

            # 0x60-0x61: Sp. Attack
            self.sp_attack = struct.unpack_from("<H", data, 0x60)[0]

            # 0x62-0x63: Sp. Defense
            self.sp_defense = struct.unpack_from("<H", data, 0x62)[0]

            self.stats = [self.max_hp, self.attack, self.defense, self.sp_attack, self.sp_defense, self.speed]


        def decrypt_data(self):
            key = self.pid ^ self.otid

            p("Key:", hex(key))

            decrypted = bytearray()
            for i in range(0, 48, 4):
                word = struct.unpack_from("<I", self.data, i)[0]
                decrypted += struct.pack("<I", word ^ key)

            self.decrypted_data = decrypted

            p("Decrypted data:", self.decrypted_data)


        def parse_substructure(self):
            order = DATA_ORDERS[self.pid % 24]

            p("Order:", order)

            g_offset = order.index("G") * 12
            a_offset = order.index("A") * 12
            e_offset = order.index("E") * 12
            m_offset = order.index("M") * 12

            # Growth substructure
            species = struct.unpack_from("<H", self.decrypted_data, g_offset)[0]

            p("Species:", species)

            if species > 905 and species - 1 < len(MONLIST):
                # this is a form
                self.form = MONLIST[species - 1]
                self.species = self.form.split()[0]
                self.species_no = MONLIST.index(self.species) + 1
            elif species - 1 > len(MONLIST):
                self.species = "Bulbasaur"
                self.species_no = 1
                self.form = None
            else:
                self.form = None
                self.species = MONLIST[species - 1]
                self.species_no = species
            # except IndexError:
            #     self.species = "Bulbasaur"
            #     self.species_no = 1

            item = struct.unpack_from("<H", self.decrypted_data, g_offset + 2)[0]
            if item != 0:
                self.item = ITEMLIST[item - 1]
            else:
                self.item = None
            self.experience = struct.unpack_from("<I", self.decrypted_data, g_offset + 4)[0]
            pp_bonuses = self.decrypted_data[g_offset + 8]
            # first 2 bits are move 1, next 2 are move 2, etc.
            self.pp_bonuses = [pp_bonuses & 0b11, (pp_bonuses >> 2) & 0b11, (pp_bonuses >> 4) & 0b11, (pp_bonuses >> 6) & 0b11]

            self.friendship = self.decrypted_data[g_offset + 9]
            self.unknown_growth = self.decrypted_data[g_offset + 10]

            # Attacks substructure
            move1 = struct.unpack_from("<H", self.decrypted_data, a_offset)[0]
            move2 = struct.unpack_from("<H", self.decrypted_data, a_offset + 2)[0]
            move3 = struct.unpack_from("<H", self.decrypted_data, a_offset + 4)[0]
            move4 = struct.unpack_from("<H", self.decrypted_data, a_offset + 6)[0]

            self.moves = []
            for move in [move1, move2, move3, move4]:
                if move != 0:
                    self.moves.append(MOVELIST[move - 1])
                else:
                    self.moves.append(None)

            self.pp1 = self.decrypted_data[a_offset + 8]
            self.pp2 = self.decrypted_data[a_offset + 9]
            self.pp3 = self.decrypted_data[a_offset + 10]
            self.pp4 = self.decrypted_data[a_offset + 11]

            self.pp = [self.pp1, self.pp2, self.pp3, self.pp4]

            # p(move1, move2, move3, move4)
            self.base_pp = [MOVEPPLIST[move - 1] for move in [move1, move2, move3, move4]]
            # p(self.base_pp)
            self.max_pp = [calc_pp_bonus(pp, bonus) for pp, bonus in zip(self.base_pp, self.pp_bonuses)]

            # EVs substructure
            self.hp_ev = self.decrypted_data[e_offset]
            self.attack_ev = self.decrypted_data[e_offset + 1]
            self.defense_ev = self.decrypted_data[e_offset + 2]
            self.speed_ev = self.decrypted_data[e_offset + 3]
            self.sp_attack_ev = self.decrypted_data[e_offset + 4]
            self.sp_defense_ev = self.decrypted_data[e_offset + 5]
            self.coolness_ev = self.decrypted_data[e_offset + 6]
            self.beauty_ev = self.decrypted_data[e_offset + 7]
            self.cuteness_ev = self.decrypted_data[e_offset + 8]
            self.smartness_ev = self.decrypted_data[e_offset + 9]
            self.toughness_ev = self.decrypted_data[e_offset + 10]
            self.feel_ev = self.decrypted_data[e_offset + 11]

            self.evs = [self.hp_ev, self.attack_ev, self.defense_ev, self.sp_attack_ev, self.sp_defense_ev, self.speed_ev]

            # Misc substructure
            self.pokerus = self.decrypted_data[m_offset]
            self.met_location = self.decrypted_data[m_offset + 1]
            self.origins_info = struct.unpack_from("<H", self.decrypted_data, m_offset + 2)[0]
            # IVs, egg, ability
            self.ivea = struct.unpack_from("<I", self.decrypted_data, m_offset + 4)[0]

            # IVs are lowest 30 bits
            ivs = self.ivea & 0x3FFFFFFF
            # Egg flag is bit 30
            self.egg = bool(self.ivea & 0x40000000)
            # Ability is bit 31
            self.ability = self.ivea & 0x80000000

            # split IVs into 5 bytes each
            self.hp_iv = ivs & 0x1F
            self.attack_iv = (ivs >> 5) & 0x1F
            self.defense_iv = (ivs >> 10) & 0x1F
            self.speed_iv = (ivs >> 15) & 0x1F
            self.sp_attack_iv = (ivs >> 20) & 0x1F
            self.sp_defense_iv = (ivs >> 25) & 0x1F

            self.ivs = [self.hp_iv, self.attack_iv, self.defense_iv, self.sp_attack_iv, self.sp_defense_iv, self.speed_iv]

    return Pokemon
