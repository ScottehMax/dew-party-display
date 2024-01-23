from typing import Optional, Protocol, TypeVar


class Gen1Protocol(Protocol):
    species: str
    species_no: int
    current_hp: int
    max_hp: int
    level: int
    status: Optional[str]

    moves: list[Optional[str]]
    pp: list[int]
    max_pp: list[int]


class PokemonProtocol(Protocol):
    pid: int
    nature: str
    otid: int
    sid: int
    id: int
    shiny: bool
    nickname: str
    language: int
    misc_flags: int
    ot_name: str
    markings: int
    checksum: int
    unused: bytes
    data: bytes
    decrypted_data: bytearray
    form: Optional[str]
    species: str
    species_no: int
    item: Optional[str]
    experience: int
    pp_bonuses: list[int]
    friendship: int
    unknown_growth: int
    moves: list[Optional[str]]
    pp1: int
    pp2: int
    pp3: int
    pp4: int
    pp: list[int]
    base_pp: list[int]
    max_pp: list[int]

    hp_ev: int
    attack_ev: int
    defense_ev: int
    speed_ev: int
    sp_attack_ev: int
    sp_defense_ev: int
    coolness_ev: int
    beauty_ev: int
    cuteness_ev: int
    smartness_ev: int
    toughness_ev: int
    feel_ev: int
    evs: list[int]

    pokerus: int
    met_location: int
    origins_info: int

    ivea: int
    egg: bool
    ability: int

    hp_iv: int
    attack_iv: int
    defense_iv: int
    speed_iv: int
    sp_attack_iv: int
    sp_defense_iv: int
    ivs: list[int]

    gender: str
    growth: Optional[str]
    status: Optional[str]
    level: int
    mail_id: int

    current_hp: int
    max_hp: int
    attack: int
    defense: int
    speed: int
    sp_attack: int
    sp_defense: int
    stats: list[int]

    def __init__(self, data: bytes) -> None:
        ...

    def decrypt_data(self) -> None:
        ...

    def parse_substructure(self) -> None:
        ...
