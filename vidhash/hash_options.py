from __future__ import annotations
import dataclasses
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import imagehash
import numpy as np

if TYPE_CHECKING:
    from PIL.Image import Image


class HashSettings(ABC):
    @property
    @abstractmethod
    def video_size(self) -> int:
        pass

    @property
    @abstractmethod
    def blank_hash(self) -> imagehash.ImageHash:
        pass

    @abstractmethod
    def hash_image(self, img: Image) -> imagehash.ImageHash:
        pass


class DHash(HashSettings):
    def __init__(self, hash_size: int) -> None:
        self.hash_size = hash_size

    def hash_image(self, img: Image) -> imagehash.ImageHash:
        return imagehash.dhash(img, hash_size=self.hash_size)

    @property
    def video_size(self) -> int:
        return self.hash_size * 4

    @property
    def blank_hash(self) -> imagehash.ImageHash:
        return imagehash.ImageHash(np.zeros([self.hash_size, self.hash_size], dtype=bool))


@dataclasses.dataclass
class HashOptions:  # TODO: immutable
    fps: float = 5
    settings: HashSettings = DHash(8)
