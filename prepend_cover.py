#!/usr/bin/env python3

import argparse
import subprocess
from pathlib import Path
import sys


VIDEO_SUFFIXES = {".mp4"}
COVER_SUFFIXES = {".jpg", ".jpeg", ".png"}


def get_video_fps(video_path):
    """
    Detect source video FPS using ffprobe.
    """

    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]

    result = subprocess.check_output(cmd).decode().strip()

    num, den = map(int, result.split("/"))

    return num / den


def file_sort_key(path):
    stat = path.stat()
    created = getattr(stat, "st_birthtime", stat.st_mtime)
    return (max(created, stat.st_mtime), path.name)


def find_newest_file(work_folder, suffixes, label):
    candidates = [
        path
        for path in work_folder.iterdir()
        if path.is_file() and path.suffix.lower() in suffixes
    ]

    if not candidates:
        suffix_list = ", ".join(sorted(suffixes))
        print(f"ERROR: No {label} file found in {work_folder} ({suffix_list})")
        sys.exit(1)

    return max(candidates, key=file_sort_key)


def resolve_input_path(work_folder, explicit_name, suffixes, label):
    if explicit_name:
        path = work_folder / explicit_name
        if not path.exists():
            print(f"ERROR: {label} file not found: {path}")
            sys.exit(1)
        return path

    return find_newest_file(work_folder, suffixes, label)


def resolve_output_path(work_folder, explicit_name, video_path):
    if explicit_name:
        return work_folder / explicit_name

    return work_folder / f"{video_path.stem}_with_cover.mp4"


def run_ffmpeg(work_folder, input_video, input_cover, output_file, cover_duration):
    """
    Create intro-cover video using ffmpeg.
    """

    work_folder = Path(work_folder)

    video_path = resolve_input_path(work_folder, input_video, VIDEO_SUFFIXES, "video")
    cover_path = resolve_input_path(work_folder, input_cover, COVER_SUFFIXES, "cover")
    output_path = resolve_output_path(work_folder, output_file, video_path)

    fps = get_video_fps(video_path)

    print(f"Detected FPS: {fps}")
    print(f"Video: {video_path.name}")
    print(f"Cover: {cover_path.name}")
    print(f"Output: {output_path.name}")

    delay_ms = int(cover_duration * 1000)

    # stereo-safe audio delay
    audio_delay = f"{delay_ms}|{delay_ms}"

    filter_complex = (
        f"[0:v]fps={fps},format=yuv420p[v0];"
        f"[1:v]fps={fps},format=yuv420p[v1];"
        f"[v0][v1]concat=n=2:v=1:a=0[v];"
        f"[1:a]adelay={audio_delay},asetpts=PTS-STARTPTS[a]"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-t",
        str(cover_duration),
        "-i",
        str(cover_path),
        "-i",
        str(video_path),
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-map",
        "[a]",
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-preset",
        "fast",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output_path),
    ]

    print("\nRunning ffmpeg command:\n")
    print(" ".join(cmd))
    print()

    subprocess.run(cmd, check=True)

    print("\nDone!")
    print(f"Output file: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Prepend a cover image to a video."
    )

    parser.add_argument(
        "--work-folder",
        default=".",
        help="Folder containing input/output files (default: current directory)",
    )

    parser.add_argument(
        "--video",
        help="Input video filename (default: newest .mp4 in work folder)",
    )

    parser.add_argument(
        "--cover",
        help="Input cover filename (default: newest .jpg/.jpeg/.png in work folder)",
    )

    parser.add_argument(
        "--output",
        help="Output video filename (default: <video_stem>_with_cover.mp4)",
    )

    parser.add_argument(
        "--cover-duration",
        type=float,
        default=0.5,
        help="Cover duration in seconds (default: 0.5)",
    )

    args = parser.parse_args()

    run_ffmpeg(
        work_folder=args.work_folder,
        input_video=args.video,
        input_cover=args.cover,
        output_file=args.output,
        cover_duration=args.cover_duration,
    )


if __name__ == "__main__":
    main()
