import vidhash
from vidhash.match_options import FrameCountMatch, PercentageMatch, DurationMatch


async def test_few_frames_absolute(butterfly_react_clip, butterfly_react_2sec_overlap_clip):
    react_hash = await vidhash.hash_video(str(butterfly_react_clip))
    overlap_hash = await vidhash.hash_video(str(butterfly_react_2sec_overlap_clip))
    match = FrameCountMatch(count_overlap=5)
    assert match.check_match(react_hash, overlap_hash)


async def test_many_frames_absolute(butterfly_react_clip, butterfly_react_2sec_overlap_clip):
    react_hash = await vidhash.hash_video(str(butterfly_react_clip))
    overlap_hash = await vidhash.hash_video(str(butterfly_react_2sec_overlap_clip))
    match = FrameCountMatch(count_overlap=20)
    assert not match.check_match(react_hash, overlap_hash)


async def test_low_percentage(butterfly_react_clip, butterfly_react_2sec_overlap_clip):
    react_hash = await vidhash.hash_video(str(butterfly_react_clip))
    overlap_hash = await vidhash.hash_video(str(butterfly_react_2sec_overlap_clip))
    match = PercentageMatch(percentage_overlap=20)
    assert match.check_match(react_hash, overlap_hash)


async def test_high_percentage(butterfly_react_clip, butterfly_react_2sec_overlap_clip):
    react_hash = await vidhash.hash_video(str(butterfly_react_clip))
    overlap_hash = await vidhash.hash_video(str(butterfly_react_2sec_overlap_clip))
    match = PercentageMatch(percentage_overlap=30)
    assert not match.check_match(react_hash, overlap_hash)


async def test_short_duration(butterfly_react_clip, butterfly_react_2sec_overlap_clip):
    react_hash = await vidhash.hash_video(str(butterfly_react_clip))
    overlap_hash = await vidhash.hash_video(str(butterfly_react_2sec_overlap_clip))
    match = DurationMatch(time_overlap=1)
    assert match.check_match(react_hash, overlap_hash)


async def test_long_duration(butterfly_react_clip, butterfly_react_2sec_overlap_clip):
    react_hash = await vidhash.hash_video(str(butterfly_react_clip))
    overlap_hash = await vidhash.hash_video(str(butterfly_react_2sec_overlap_clip))
    match = DurationMatch(time_overlap=3)
    assert not match.check_match(react_hash, overlap_hash)
