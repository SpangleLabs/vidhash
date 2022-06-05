from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from vidhash.match_options import DEFAULT_MATCH_OPTS

if TYPE_CHECKING:
    from typing import Iterator, List, Set

    from vidhash.frame_hash import FrameHash
    from vidhash.hash_options import HashOptions
    from vidhash.match_options import MatchOptions


@dataclasses.dataclass
class VideoHash:
    image_hashes: List[FrameHash]
    video_length: float
    hash_options: HashOptions

    @property
    def hash_set(self) -> Set[FrameHash]:
        return set(self.image_hashes)

    def matching_hashes(
        self, other_hash: FrameHash, hamming_dist: int = 0, ignore_blank: bool = False
    ) -> Iterator[FrameHash]:
        hash_set = self.hash_set.copy()
        if ignore_blank:
            hash_set.discard(self.hash_options.settings.blank_hash)
        for image_hash in hash_set:
            if image_hash.similar_to(other_hash, hamming_dist):
                yield image_hash

    def contains_hash(self, other_hash: FrameHash, hamming_dist: int = 0, ignore_blank: bool = False) -> bool:
        return any(self.matching_hashes(other_hash, hamming_dist, ignore_blank))

    def matches_hash(self, other_hash: VideoHash, match_options: MatchOptions = None) -> bool:
        match_options = match_options or DEFAULT_MATCH_OPTS
        return match_options.check_match(self, other_hash)

    def has_blank_frame(self) -> bool:
        return self.hash_options.settings.blank_hash in self.hash_set
