"""Simple PNG/GIF visualizer for single-tape Turing machine runs."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .tm_engine import Configuration, SingleTapeTM


BACKGROUND = (247, 249, 252)
TEXT = (33, 37, 41)
MUTED = (92, 99, 112)
CELL_FILL = (255, 255, 255)
CELL_BORDER = (122, 132, 148)
HEAD_FILL = (223, 241, 255)
HEAD_BORDER = (32, 116, 184)
ARROW = (210, 74, 67)


def render_configuration(
    configuration: Configuration,
    output_path: str | Path,
    step_number: int | None = None,
) -> Path:
    """Render one configuration to a PNG file."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    symbols, head_index = _normalize_tape(configuration)
    font = ImageFont.load_default()
    title_font = ImageFont.load_default()

    cell_size = 52
    margin = 36
    top = 92
    width = max(520, margin * 2 + len(symbols) * cell_size)
    height = 235

    image = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(image)

    step_text = "" if step_number is None else f"Step {step_number}  |  "
    draw.text(
        (margin, 28),
        f"{step_text}State: {configuration.state}",
        fill=TEXT,
        font=title_font,
    )
    draw.text((margin, 54), "Tape", fill=MUTED, font=font)

    for index, symbol in enumerate(symbols):
        x0 = margin + index * cell_size
        y0 = top
        x1 = x0 + cell_size
        y1 = y0 + cell_size
        is_head = index == head_index
        draw.rectangle(
            (x0, y0, x1, y1),
            fill=HEAD_FILL if is_head else CELL_FILL,
            outline=HEAD_BORDER if is_head else CELL_BORDER,
            width=3 if is_head else 1,
        )
        _center_text(draw, (x0, y0, x1, y1), symbol, font, TEXT)

    head_center_x = margin + head_index * cell_size + cell_size // 2
    arrow_top = top + cell_size + 14
    draw.line(
        (head_center_x, arrow_top + 30, head_center_x, arrow_top),
        fill=ARROW,
        width=3,
    )
    draw.polygon(
        [
            (head_center_x, arrow_top),
            (head_center_x - 8, arrow_top + 10),
            (head_center_x + 8, arrow_top + 10),
        ],
        fill=ARROW,
    )
    _center_text(
        draw,
        (head_center_x - 48, arrow_top + 34, head_center_x + 48, arrow_top + 52),
        f"head {configuration.head_position}",
        font,
        MUTED,
    )

    image.save(output)
    return output


def render_history(
    history: list[Configuration],
    output_dir: str | Path,
    prefix: str = "frame",
    max_frames: int | None = None,
) -> list[Path]:
    """Render a run history as numbered PNG files."""

    selected = history if max_frames is None else history[:max_frames]
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    for step, configuration in enumerate(selected):
        path = output / f"{prefix}_{step:03d}.png"
        paths.append(render_configuration(configuration, path, step_number=step))
    return paths


def make_gif(
    frame_paths: list[str | Path],
    output_path: str | Path,
    duration: int = 450,
) -> Path:
    """Create an animated GIF from rendered PNG frame paths."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    frames = [Image.open(path) for path in frame_paths]
    if not frames:
        raise ValueError("At least one frame is required")
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
    )
    for frame in frames:
        frame.close()
    return output


def render_machine_run(
    machine_path: str | Path,
    input_string: str,
    output_dir: str | Path,
    max_steps: int = 1000,
    max_frames: int = 8,
    prefix: str = "frame",
) -> list[Path]:
    """Run a single-tape machine and render the first configurations."""

    tm = SingleTapeTM.from_yaml(machine_path)
    result = tm.run(input_string, max_steps=max_steps)
    return render_history(result.history, output_dir, prefix=prefix, max_frames=max_frames)


def _normalize_tape(configuration: Configuration) -> tuple[list[str], int]:
    symbols = list(configuration.tape) or ["B"]
    head_position = configuration.head_position

    if head_position < 0:
        symbols = ["B"] * abs(head_position) + symbols
        return symbols, 0
    if head_position >= len(symbols):
        symbols.extend(["B"] * (head_position - len(symbols) + 1))
    return symbols, head_position


def _center_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
) -> None:
    left, top, right, bottom = box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = left + ((right - left) - text_width) / 2
    y = top + ((bottom - top) - text_height) / 2
    draw.text((x, y), text, fill=fill, font=font)


def main() -> None:
    """Command line helper for generating demo frames."""

    import argparse

    parser = argparse.ArgumentParser(description="Render Turing machine frames.")
    parser.add_argument("machine", help="Path to a single-tape machine YAML file")
    parser.add_argument("input", help="Input string")
    parser.add_argument("--output-dir", default="docs/images")
    parser.add_argument("--max-steps", type=int, default=1000)
    parser.add_argument("--max-frames", type=int, default=8)
    parser.add_argument("--prefix", default="frame")
    parser.add_argument("--gif", default="")
    args = parser.parse_args()

    paths = render_machine_run(
        args.machine,
        args.input,
        args.output_dir,
        max_steps=args.max_steps,
        max_frames=args.max_frames,
        prefix=args.prefix,
    )
    if args.gif:
        make_gif(paths, args.gif)

    print(f"rendered {len(paths)} frame(s)")


if __name__ == "__main__":
    main()
