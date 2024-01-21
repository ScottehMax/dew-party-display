from typing import Protocol

from PIL.Image import Image


class Theme(Protocol):
    sprites: str

    def set_sprite_folder(self, sprites_folder: str) -> None:
        ...

    def create_image_6x1(self, results: list[dict[str, str]]) -> Image:
        ...

    def create_image_3x2(self, results: list[dict[str, str]]) -> Image:
        ...
