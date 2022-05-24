from __future__ import annotations
import dataclasses
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import List, Set, Iterator
    import imagehash
    from vidhash.hash_options import HashOptions


@dataclasses.dataclass
class VideoHash:
    image_hashes: List[imagehash.ImageHash]
    video_length: float
    hash_options: HashOptions

    @property
    def hash_set(self) -> Set[imagehash.ImageHash]:
        return set(self.image_hashes)

    def matching_hashes(self, other_hash: imagehash.ImageHash, hamming_dist: int = 0) -> Iterator[imagehash.ImageHash]:
        for image_hash in self.hash_set:
            if (image_hash - other_hash) <= hamming_dist:
                yield image_hash

    def contains_hash(self, other_hash: imagehash.ImageHash, hamming_dist: int = 0) -> bool:
        return any(self.matching_hashes(other_hash, hamming_dist))
