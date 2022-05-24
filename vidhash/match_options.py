from __future__ import annotations
import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vidhash.video_hash import VideoHash


class MatchOptions(ABC):
    hamming_dist: int = 0

    @abstractmethod
    def check_match(self, hash1: VideoHash, hash2: VideoHash) -> bool:
        pass


def _has_overlap(hash1: VideoHash, hash2: VideoHash, required_overlap: float, hamming_distance: int) -> bool:
    overlaps = 0
    for image_hash in hash1.hash_set:
        if hash2.contains_hash(image_hash, hamming_distance):
            overlaps += 1
            if overlaps >= required_overlap:
                return True
    return False


class PercentageMatch(MatchOptions):
    percentage_overlap: float = 50
    ignore_blank: bool = True  # TODO

    def check_match(self, hash1: VideoHash, hash2: VideoHash) -> bool:
        required_overlap = self.percentage_overlap * min(len(hash1.hash_set), len(hash2.hash_set)) / 100
        return _has_overlap(hash1, hash2, required_overlap, self.hamming_dist)


class AbsoluteMatch(MatchOptions):
    count_overlap: int = 1
    ignore_blank: bool = True  # TODO

    def check_match(self, hash1: VideoHash, hash2: VideoHash) -> bool:
        required_overlap = min(self.count_overlap, len(hash1.hash_set), len(hash2.hash_set))
        return _has_overlap(hash1, hash2, required_overlap, self.hamming_dist)


class DurationMatch(MatchOptions):
    time_overlap: float = 0

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
            if (frame1 - frame2) > self.hamming_dist:
                return False
            match_count += 1
            if match_count >= target_length:
                return True
        return match_count >= target_length

    def check_match(self, hash1: VideoHash, hash2: VideoHash) -> bool:
        frame_count = min(
            math.ceil(hash1.hash_options.fps * self.time_overlap), len(hash1.image_hashes), len(hash2.image_hashes)
        )
        shorter, longer = (hash1, hash2) if hash1.video_length < hash2.video_length else (hash2, hash1)
        for frame_num1 in range(len(shorter.image_hashes)):
            for frame_num2 in range(len(longer.image_hashes)):
                if self._check_match_from(shorter, frame_num1, longer, frame_num2, frame_count):
                    return True
        return False
