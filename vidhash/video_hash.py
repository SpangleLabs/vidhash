from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from vidhash.match_options import DEFAULT_MATCH_OPTS

if TYPE_CHECKING:
    from typing import Iterator, List, Set

    import imagehash

    from vidhash.hash_options import HashOptions
    from vidhash.match_options import MatchOptions


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

    def matches_hash(self, other_hash: VideoHash, match_options: MatchOptions = None) -> bool:
        match_options = match_options or DEFAULT_MATCH_OPTS
        return match_options.check_match(self, other_hash)
