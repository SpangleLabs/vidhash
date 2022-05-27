import pytest

import vidhash
from vidhash import VideoHash
from vidhash.match_options import FrameCountMatch, DEFAULT_MATCH_OPTS, PercentageMatch


async def test_long_video_length(long_video):
    assert long_video is not None


async def test_hash_scene(butterfly_react_clip):
    video_hash = await vidhash.hash_video(str(butterfly_react_clip))
    assert video_hash is not None
    assert isinstance(video_hash, VideoHash)


async def test_match_self(butterfly_react_clip):
    hash1 = await vidhash.hash_video(str(butterfly_react_clip))
    hash2 = await vidhash.hash_video(str(butterfly_react_clip))
    assert hash1.matches_hash(hash2)


async def test_match_self_explicit_match(butterfly_react_clip):
    hash1 = await vidhash.hash_video(str(butterfly_react_clip))
    hash2 = await vidhash.hash_video(str(butterfly_react_clip))
    match = PercentageMatch(3, 20)
    assert match.check_match(hash1, hash2)


async def test_match_self_total_match(butterfly_react_clip):
    hash1 = await vidhash.hash_video(str(butterfly_react_clip))
    hash2 = await vidhash.hash_video(str(butterfly_react_clip))
    match = PercentageMatch(0, 100)
    assert match.check_match(hash1, hash2)


async def test_match_low_resolution(butterfly_react_clip, butterfly_react_clip_low_res):
    high_res = await vidhash.hash_video(str(butterfly_react_clip))
    low_res = await vidhash.hash_video(str(butterfly_react_clip_low_res))
    assert high_res.matches_hash(low_res)
    assert low_res.matches_hash(high_res)


async def test_match_reverse(butterfly_react_clip, butterfly_react_reverse):
    forward = await vidhash.hash_video(str(butterfly_react_clip))
    reverse = await vidhash.hash_video(str(butterfly_react_reverse))
    assert forward.matches_hash(reverse)
    assert reverse.matches_hash(forward)


async def test_two_different_scenes(butterfly_react_clip, butterfly_kill_clip):
    react_hash = await vidhash.hash_video(str(butterfly_react_clip))
    kill_hash = await vidhash.hash_video(str(butterfly_kill_clip))
    assert not react_hash.matches_hash(kill_hash)


async def test_blank_match(intro_clip, credits_clip):
    intro_hash = await vidhash.hash_video(str(intro_clip))
    credits_hash = await vidhash.hash_video(str(credits_clip))
    match = FrameCountMatch(hamming_dist=0, count_overlap=1, ignore_blank=False)
    assert match.check_match(intro_hash, credits_hash)


async def test_blank_skip_no_match(intro_clip, credits_clip):
    intro_hash = await vidhash.hash_video(str(intro_clip))
    credits_hash = await vidhash.hash_video(str(credits_clip))
    match = FrameCountMatch(hamming_dist=0, count_overlap=1, ignore_blank=True)
    assert not match.check_match(intro_hash, credits_hash)


async def test_scene_matches_subscene(butterfly_react_clip, both_butterflies_clip):
    react_hash = await vidhash.hash_video(str(butterfly_react_clip))
    both_hash = await vidhash.hash_video(str(both_butterflies_clip))
    assert react_hash.matches_hash(both_hash)
    assert both_hash.matches_hash(react_hash)


# - - cut two scenes from big buck bunny, ensure they don't match.
# - - cut two scenes with two second overlap, check different match metrics. 5 frames, 20 frames, 5%, 15%, 1 second, 3 second.
# - - check scene matches itself
# - - check small scene matches full video?
