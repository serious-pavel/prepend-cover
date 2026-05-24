# prepend-cover

`prepend-cover` is a small ffmpeg-based command that prepends a cover image to a video while keeping the video audio aligned and preserving the source video FPS.

## Requirements

- Python 3.9 or newer
- `ffmpeg`
- `ffprobe`

## Install

The project uses a local virtual environment in `.venv`. If it already exists, you can reuse it. If you want to create a clean one from the project directory:

```bash
python3 -m venv .venv
```

Then install the user-local command wrapper into a PATH directory:

```bash
mkdir -p "$HOME/.local/bin"
ln -sf "$PWD/bin/prepend-cover" "$HOME/.local/bin/prepend-cover"
```

Make sure `~/.local/bin` is on your `PATH`. Add this to your shell startup file if it is not already there. For `zsh`, `~/.zshrc` is usually the right place:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Use

Run the command in a folder that contains the source files:

```bash
prepend-cover
```

By default, it picks:

- the newest `.mp4` file in the folder
- the newest `.jpg`, `.jpeg`, or `.png` file in the folder
- an output name based on the video file, for example `movie_with_cover.mp4`

You can still override any of these:

```bash
prepend-cover --work-folder /path/to/files --video input.mp4 --cover cover.png --output output.mp4
```

## Uninstall

Remove the user-local command wrapper from your PATH directory:

```bash
rm -f "$HOME/.local/bin/prepend-cover"
```

Remove the project virtual environment if you do not need it:

```bash
rm -rf .venv
```
