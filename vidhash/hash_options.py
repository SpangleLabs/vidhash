from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

import imagehash
import numpy as np

if TYPE_CHECKING:
    from typing import Optional

    from PIL.Image import Image


class HashSettings(ABC):
    @abstractmethod
    def get_video_size(self) -> int:
        pass

    @property
    @abstractmethod
    def blank_hash(self) -> imagehash.ImageHash:
        pass

    @abstractmethod
    def hash_image(self, img: Image) -> imagehash.ImageHash:
        pass


@dataclass(eq=True, frozen=True)
class DHash(HashSettings):
    hash_size: int = 8
    video_size: Optional[int] = None

    def hash_image(self, img: Image) -> imagehash.ImageHash:
        return imagehash.dhash(img, hash_size=self.hash_size)

    def get_video_size(self) -> int:
        if self.video_size is None:
            return self.hash_size * 25
        return self.video_size

    @property
    def blank_hash(self) -> imagehash.ImageHash:
        return imagehash.ImageHash(np.zeros([self.hash_size, self.hash_size], dtype=bool))


@dataclass(eq=True, frozen=True)
class HashOptions:
    fps: float = 5
    settings: HashSettings = DHash(8)


DEFAULT_HASH_OPTS = HashOptions()
