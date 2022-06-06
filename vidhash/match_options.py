from __future__ import annotations

import logging
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, Tuple

    from vidhash.frame_hash import FrameHash
    from vidhash.video_hash import VideoHash


logger = logging.getLogger(__name__)


class MatchException(ValueError):
    pass


@dataclass(eq=True, frozen=True)  # type: ignore[misc]
class MatchOptions(ABC):
    hamming_dist: int = 3

    def check_match(self, hash1: VideoHash, hash2: VideoHash) -> bool:
        logger.info("Checking match between hashes using %s", self.__class__.__name__)
        if hash1.hash_options != hash2.hash_options:
            raise MatchException("Video hashes were not created with the same hash options, so cannot be compared.")
        return self._check_match(hash1, hash2)

    @abstractmethod
    def _check_match(self, hash1: VideoHash, hash2: VideoHash) -> bool:
        pass

    def _has_overlap(
        self, frame_hashes: Iterable[FrameHash], hash2: VideoHash, required_overlap: float, ignore_blank: bool
    ) -> bool:
        overlaps = 0
        for image_hash in frame_hashes:
            if hash2.contains_hash(image_hash, self.hamming_dist, ignore_blank):
                overlaps += 1
                logger.debug("Found %s of %s overlaps", overlaps, required_overlap)
                if overlaps >= required_overlap:
                    return True
        return False


def _shorter_longer(hash1: VideoHash, hash2: VideoHash) -> Tuple[VideoHash, VideoHash]:
    return (hash1, hash2) if hash1.video_length < hash2.video_length else (hash2, hash1)


@dataclass(eq=True, frozen=True)
class PercentageMatch(MatchOptions):
    percentage_overlap: float = 30
    ignore_blank: bool = True

    def _check_match(self, hash1: VideoHash, hash2: VideoHash) -> bool:
        required_overlap = self.percentage_overlap * min(len(hash1.image_hashes), len(hash2.image_hashes)) / 100
        logger.debug(
            "Match will require at least %s frames with hamming distance %s", required_overlap, self.hamming_dist
        )
        shorter, longer = _shorter_longer(hash1, hash2)
        image_hashes = shorter.image_hashes.copy()
        if self.ignore_blank:
            blank_hash = shorter.hash_options.settings.blank_hash
            image_hashes = [frame_hash for frame_hash in image_hashes if frame_hash != blank_hash]
        return self._has_overlap(image_hashes, longer, required_overlap, self.ignore_blank)


@dataclass(eq=True, frozen=True)
class FrameCountMatch(MatchOptions):
    count_overlap: int = 3
    ignore_blank: bool = True

    def _check_match(self, hash1: VideoHash, hash2: VideoHash) -> bool:
        required_overlap = min(self.count_overlap, len(hash1.hash_set), len(hash2.hash_set))
        logger.debug(
            "Match will require at least %s frames with hamming distance %s", required_overlap, self.hamming_dist
        )
        hash_set = hash1.hash_set.copy()
        if self.ignore_blank:
            hash_set.discard(hash1.hash_options.settings.blank_hash)
        return self._has_overlap(hash_set, hash2, required_overlap, self.ignore_blank)


@dataclass(eq=True, frozen=True)
class DurationMatch(MatchOptions):
    time_overlap: float = 3

    def _check_match_from(
        self,
        hash1: VideoHash,
        start_frame1: int,
        hash2: VideoHash,
        start_frame2: int,
        target_length: int,
    ) -> bool:
        match_count = 0
        remaining_frames1 = hash1.image_hashes[start_frame1:]
        remaining_frames2 = hash2.image_hashes[start_frame2:]
        if len(remaining_frames1) < target_length or len(remaining_frames2) < target_length:
            return False
        for frame1, frame2 in zip(remaining_frames1, remaining_frames2):
            if not frame1.similar_to(frame2, self.hamming_dist):
                return False
            match_count += 1
            if match_count >= target_length:
                return True
        return match_count >= target_length

    def _check_match(self, hash1: VideoHash, hash2: VideoHash) -> bool:
        frame_count = min(
            math.ceil(hash1.hash_options.fps * self.time_overlap), len(hash1.image_hashes), len(hash2.image_hashes)
        )
        logger.debug(
            "Will need at least %s frames in a row which match within %s hamming distance",
            frame_count,
            self.hamming_dist,
        )
        shorter, longer = _shorter_longer(hash1, hash2)
        for frame_num1 in range(len(shorter.image_hashes)):
            for frame_num2 in range(len(longer.image_hashes)):
                if self._check_match_from(shorter, frame_num1, longer, frame_num2, frame_count):
                    return True
        return False


DEFAULT_MATCH_OPTS = PercentageMatch(3, 30)
