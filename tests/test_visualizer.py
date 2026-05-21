from pathlib import Path

from PIL import Image

from turinglab import SingleTapeTM
from turinglab.visualizer import make_gif, render_history


ROOT = Path(__file__).resolve().parents[1]
MACHINES = ROOT / "machines"


def test_visualizer_renders_png_frames(tmp_path):
    tm = SingleTapeTM.from_yaml(MACHINES / "binary_increment.yaml")
    result = tm.run("1011", max_steps=100)

    paths = render_history(result.history, tmp_path, prefix="demo", max_frames=5)

    assert len(paths) == 5
    for path in paths:
        assert path.exists()
        with Image.open(path) as image:
            assert image.format == "PNG"
            assert image.size[0] >= 520
            assert image.size[1] >= 200


def test_visualizer_creates_gif(tmp_path):
    tm = SingleTapeTM.from_yaml(MACHINES / "binary_increment.yaml")
    result = tm.run("1", max_steps=20)
    paths = render_history(result.history, tmp_path, prefix="gif_demo", max_frames=4)

    gif_path = make_gif(paths, tmp_path / "demo.gif")

    assert gif_path.exists()
    with Image.open(gif_path) as image:
        assert image.format == "GIF"
