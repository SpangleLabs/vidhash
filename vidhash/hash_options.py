from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

import imagehash
import numpy as np

from vidhash.frame_hash import SimpleImageHash

if TYPE_CHECKING:
    from typing import Optional

    from PIL.Image import Image

    from vidhash.frame_hash import FrameHash


class HashSettings(ABC):
    @abstractmethod
    def get_video_size(self) -> int:
        pass

    @property
    @abstractmethod
    def blank_hash(self) -> FrameHash:
        pass

    @abstractmethod
    def hash_image(self, img: Image) -> FrameHash:
        pass


@dataclass(eq=True, frozen=True)
class DHash(HashSettings):
    hash_size: int = 8
    video_size: Optional[int] = None

    def hash_image(self, img: Image) -> FrameHash:
        return SimpleImageHash(imagehash.dhash(img, hash_size=self.hash_size))

    def get_video_size(self) -> int:
        if self.video_size is None:
            return self.hash_size * 25
        return self.video_size

    @property
    def blank_hash(self) -> FrameHash:
        return SimpleImageHash(imagehash.ImageHash(np.zeros([self.hash_size, self.hash_size], dtype=bool)))


@dataclass(eq=True, frozen=True)
class HashOptions:
    fps: float = 5
    settings: HashSettings = DHash(8)


DEFAULT_HASH_OPTS = HashOptions()
