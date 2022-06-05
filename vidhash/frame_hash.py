from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import imagehash


class FrameHash(ABC):
    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass

    @abstractmethod
    def __hash__(self) -> int:
        pass

    @abstractmethod
    def similar_to(self, other: FrameHash, hamming_dist: float) -> bool:
        pass


class SimpleImageHash(FrameHash):
    def __init__(self, image_hash: imagehash.ImageHash) -> None:
        self.image_hash = image_hash

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SimpleImageHash) and other.image_hash == self.image_hash

    def __hash__(self) -> int:
        return hash((SimpleImageHash, self.image_hash))

    def similar_to(self, other: FrameHash, hamming_dist: float) -> bool:
        if not isinstance(other, SimpleImageHash):
            raise ValueError(f"Can't compare {self.__class__.__name__} with {other.__class__.__name__}")
        return (self.image_hash - other.image_hash) <= hamming_dist
