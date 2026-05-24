#!/usr/bin/env python3

import argparse
import subprocess
from pathlib import Path
import sys


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


def run_ffmpeg(work_folder, input_video, input_cover, output_file, cover_duration):
    """
    Create intro-cover video using ffmpeg.
    """

    work_folder = Path(work_folder)

    video_path = work_folder / input_video
    cover_path = work_folder / input_cover
    output_path = work_folder / output_file

    if not video_path.exists():
        print(f"ERROR: Video file not found: {video_path}")
        sys.exit(1)

    if not cover_path.exists():
        print(f"ERROR: Cover file not found: {cover_path}")
        sys.exit(1)

    fps = get_video_fps(video_path)

    print(f"Detected FPS: {fps}")

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
        required=True,
        help="Input video filename",
    )

    parser.add_argument(
        "--cover",
        required=True,
        help="Input cover image filename",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output video filename",
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
