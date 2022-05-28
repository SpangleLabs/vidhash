import os.path
from pathlib import Path

import pytest
import requests

import vidhash.func

SAMPLE_VIDEOS = [
    "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",  # 158mb, 596s
    "https://storage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",  # 169mb, 653s
    "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",  # 2.4mb, 15s
    "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",  # 2.3mb, 15s
    "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",  # 13mb, 60s
    "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",  # 23mb, 15s
    "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",  # 22.5mb, 15s
    "https://storage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",  # 190mb, 888s
    "https://storage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4",  # 48mb, 594s
    "https://storage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",  # 185mb, 734s
]

TEST_DIR = Path(vidhash.func.TEMP_DIR) / "tests"
BIG_BUCK_BUNNY_FILENAME = "BigBuckBunny.mp4"
BIG_BUCK_BUNNY_URL = "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"  # 158mb, 596s
INTRO_SCENE_FILENAME = "IntroScene.mp4"
BUTTERFLY_REACT_SCENE = "ButterflyReact.mp4"
BUTTERFLY_REACT_OVERLAP_SCENE = "ButterflyReactOverlap.mp4"
BUTTERFLY_REACT_LOW_RES = "ButterflyReactSmol.mp4"
BUTTERFLY_REACT_REVERSE = "ButterflyReactReverse.mp4"
BOTH_BUTTERFLIES_SCENES = "ButterflyBoth.mp4"
BUTTERFLY_KILL_SCENE = "ButterflyKill.mp4"
CREDITS_SCENE_FILENAME = "CreditsScene.mp4"


@pytest.fixture
def long_video() -> Path:
    video_path = TEST_DIR / BIG_BUCK_BUNNY_FILENAME
    if not os.path.exists(video_path):
        resp = requests.get(BIG_BUCK_BUNNY_URL)
        os.makedirs(TEST_DIR, exist_ok=True)
        with open(video_path, "wb") as f:
            f.write(resp.content)
    return video_path


async def cut_video(input_path: Path, output_path: Path, start: int, end: int) -> None:
    await vidhash.func._run_ffmpeg(inputs={str(input_path): None}, outputs={str(output_path): f"-ss {start} -to {end}"})


@pytest.fixture
async def intro_clip(long_video: Path) -> Path:
    # Intro clip of the video, should include a blank frame
    scene_start = 0
    scene_end = 15
    video_path = TEST_DIR / INTRO_SCENE_FILENAME
    if not os.path.exists(video_path):
        await cut_video(long_video, video_path, scene_start, scene_end)
    return video_path


@pytest.fixture
async def butterfly_react_clip(long_video: Path) -> Path:
    # Small scene in the middle of the video
    scene_start = 60 + 44
    scene_end = 60 + 52
    video_path = TEST_DIR / BUTTERFLY_REACT_SCENE
    if not os.path.exists(video_path):
        await cut_video(long_video, video_path, scene_start, scene_end)
    return video_path


@pytest.fixture
async def butterfly_react_2sec_overlap_clip(long_video: Path) -> Path:
    # Small scene which overlaps with the butterfly react clip by 2 seconds
    scene_start = 60 + 50
    scene_end = 60 + 58
    video_path = TEST_DIR / BUTTERFLY_REACT_OVERLAP_SCENE
    if not os.path.exists(video_path):
        await cut_video(long_video, video_path, scene_start, scene_end)
    return video_path


@pytest.fixture
async def butterfly_react_clip_low_res(butterfly_react_clip: Path) -> Path:
    video_path = TEST_DIR / BUTTERFLY_REACT_LOW_RES
    if not os.path.exists(video_path):
        filters = ",".join(
            [
                "scale='min({0},iw)':'min({1},ih)':force_original_aspect_ratio=decrease".format(700, 700),
                "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            ]
        )
        await vidhash.func._run_ffmpeg(
            inputs={str(butterfly_react_clip): None}, outputs={str(video_path): f'-vf "{filters}"'}
        )
    return video_path


@pytest.fixture
async def butterfly_react_reverse(butterfly_react_clip: Path) -> Path:
    video_path = TEST_DIR / BUTTERFLY_REACT_REVERSE
    if not os.path.exists(video_path):
        await vidhash.func._run_ffmpeg(
            inputs={str(butterfly_react_clip): None}, outputs={str(video_path): "-vf reverse -af areverse"}
        )
    return video_path


@pytest.fixture
async def both_butterflies_clip(long_video: Path) -> Path:
    # Both butterflies scenes, should include the scene above
    scene_start = 60 + 16
    scene_end = 60 + 57
    video_path = TEST_DIR / BOTH_BUTTERFLIES_SCENES
    if not os.path.exists(video_path):
        await cut_video(long_video, video_path, scene_start, scene_end)
    return video_path


@pytest.fixture
async def butterfly_kill_clip(long_video: Path) -> Path:
    # Butterfly kill scene, shouldn't overlap with butterfly scene
    scene_start = 3 * 60 + 6
    scene_end = 3 * 60 + 18
    video_path = TEST_DIR / BUTTERFLY_KILL_SCENE
    if not os.path.exists(video_path):
        await cut_video(long_video, video_path, scene_start, scene_end)
    return video_path


@pytest.fixture
async def credits_clip(long_video: Path) -> Path:
    # Clip of the credits, with another blank frame
    scene_start = 8 * 60 + 8
    scene_end = 9 * 60 + 41
    video_path = TEST_DIR / CREDITS_SCENE_FILENAME
    if not os.path.exists(video_path):
        await cut_video(long_video, video_path, scene_start, scene_end)
    return video_path
