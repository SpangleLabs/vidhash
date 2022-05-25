from __future__ import annotations

import glob
import logging
import os
import pathlib
import shutil
import subprocess
import uuid
from dataclasses import dataclass
from multiprocessing.pool import ThreadPool
from typing import TYPE_CHECKING

import ffmpy3
from PIL import Image

from vidhash.hash_options import DEFAULT_HASH_OPTS
from vidhash.match_options import DEFAULT_MATCH_OPTS
from vidhash.video_hash import VideoHash

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple

    from vidhash.hash_options import HashOptions
    from vidhash.match_options import MatchOptions

TEMP_DIR = "vidhash_temp/"

logger = logging.getLogger(__name__)


async def _process_ffmpeg(ff: ffmpy3.FFmpeg) -> Tuple[str, str]:
    ff_process = await ff.run_async(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out_bytes, err_bytes = await ff_process.communicate()
    logger.debug("FF process ended with exit code %s", ff_process.returncode)
    await ff.wait()
    output = out_bytes.decode("utf-8", errors="replace").strip()
    error = err_bytes.decode("utf-8", errors="replace").strip()
    return output, error


async def _run_ffmpeg(
    inputs: Dict[str, Optional[str]],
    outputs: Dict[str, Optional[str]],
    global_options: Optional[List[str]] = None,
) -> Tuple[str, str]:
    logger.debug("Running FFmpeg: global=%s, inputs=%s, outputs=%s", global_options, inputs, outputs)
    ff = ffmpy3.FFmpeg(global_options=global_options, inputs=inputs, outputs=outputs)
    return await _process_ffmpeg(ff)


async def _run_ffprobe(inputs: Dict[str, Optional[str]], global_options: Optional[List[str]] = None) -> Tuple[str, str]:
    logger.debug("Running FFProbe: global=%s, inputs=%s", global_options, inputs)
    ff = ffmpy3.FFprobe(global_options=global_options, inputs=inputs)
    return await _process_ffmpeg(ff)


def _cleanup_file(path: str) -> None:
    try:
        logger.debug("Cleaning up file: %s", path)
        os.remove(path)
    except FileNotFoundError:
        pass


def _cleanup_dir(path: str) -> None:
    try:
        logger.debug("Cleaning up directory: %s", path)
        shutil.rmtree(path)
    except FileNotFoundError:
        pass


async def _decompose_video(video_path: str, decompose_path: str, fps: float, max_size: float) -> None:
    # Convert video and downscale
    output_path = str(pathlib.Path(TEMP_DIR) / f"{uuid.uuid4()}.mp4")
    filters = [
        f"scale='min({max_size},iw)':'min({max_size},ih)':force_original_aspect_ratio=decrease",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2",
    ]
    os.makedirs(TEMP_DIR, exist_ok=True)
    try:
        logger.debug("Converting and downscaling video %s to %s", video_path, output_path)
        await _run_ffmpeg(
            inputs={video_path: None},
            outputs={output_path: f"-vf \"{','.join(filters)}\""},
        )
        # Decompose it
        os.makedirs(decompose_path, exist_ok=True)
        logger.debug("Decomposing video (%s) into frames in %s at %s FPS", output_path, decompose_path, fps)
        await _run_ffmpeg(
            inputs={output_path: None},
            outputs={f"{decompose_path}/out%d.png": f"-vf fps={fps} -vsync 0"},
            global_options=["-y"],
        )
    finally:
        # Clean up the temporary video file
        _cleanup_file(output_path)


async def _video_length(video_path: str) -> float:
    logger.debug("Getting length of video %s", video_path)
    out, err = await _run_ffprobe(
        inputs={video_path: "-show_entries format=duration -of default=noprint_wrappers=1:nokey=1"},
        global_options=["-v error"],
    )
    logger.debug("Length of video %s is: %s", video_path, out)
    return float(out)


async def hash_video(video_path: str, hash_options: HashOptions = None) -> VideoHash:
    options = hash_options or DEFAULT_HASH_OPTS
    logger.info("Hashing video: %s with options: %s", video_path, hash_options)
    # Get video length
    video_length = await _video_length(video_path)
    logger.info("Got video length: %s (%s)", video_length, video_path)
    # Decompose into images
    video_id = str(uuid.uuid4())
    decompose_path = str(pathlib.Path(TEMP_DIR) / video_id)
    try:
        await _decompose_video(video_path, decompose_path, options.fps, options.settings.video_size)
        # Hash images
        image_files = glob.glob(f"{decompose_path}/*.png")
        hash_pool = ThreadPool(os.cpu_count())
        hash_list = hash_pool.map(lambda image_path: options.settings.hash_image(Image.open(image_path)), image_files)
    finally:
        _cleanup_dir(decompose_path)
    # Create VideoHash and return
    return VideoHash(hash_list, video_length, options)


@dataclass(eq=True, frozen=True)
class CheckOptions:
    hash_options: HashOptions = DEFAULT_HASH_OPTS
    match_options: MatchOptions = DEFAULT_MATCH_OPTS


async def check_match(video_path_1: str, video_path_2: str, options: CheckOptions = None) -> bool:
    options = options or CheckOptions(DEFAULT_HASH_OPTS, DEFAULT_MATCH_OPTS)
    hash1 = await hash_video(video_path_1, options.hash_options)
    hash2 = await hash_video(video_path_2, options.hash_options)
    return options.match_options.check_match(hash1, hash2)
