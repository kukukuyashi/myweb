#!/usr/bin/env python3
"""从 img/Mouse animation/ 的 PNG 序列生成 public/cursors/ 下的 64×64 动态光标 GIF。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print('需要 Pillow：pip install Pillow', file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / 'img' / 'Mouse animation'
OUT_DIR = ROOT / 'public' / 'cursors'
SIZE = 64
FRAME_MS = 33  # ~30fps
TRANSPARENT_INDEX = 255

MAPPING = {
    '普通（第二版）': 'normal.gif',
    '交互（第二版）': 'pointer.gif',
    '文本': 'text.gif',
    '加载': 'busy.gif',
}


def sort_key(path: Path) -> int:
    match = re.search(r'(\d+)\.png$', path.name, re.IGNORECASE)
    return int(match.group(1)) if match else 0


def clean_alpha(frame: Image.Image) -> Image.Image:
    """去掉半透明脏边，避免 GIF 量化后在移动时留下黑边拖影。"""
    rgba = frame.convert('RGBA')
    px = rgba.load()
    w, h = rgba.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 48:
                px[x, y] = (0, 0, 0, 0)
            elif a < 220 and r < 64 and g < 64 and b < 64:
                # 半透明黑边 → 全透明
                px[x, y] = (0, 0, 0, 0)
    return rgba


def rgba_to_palette(frame: Image.Image) -> Image.Image:
    rgba = clean_alpha(frame)
    alpha = rgba.getchannel('A')
    rgb = rgba.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=254)
    mask = alpha.point(lambda a: 255 if a <= 128 else 0)
    rgb.paste(TRANSPARENT_INDEX, mask)
    rgb.info['transparency'] = TRANSPARENT_INDEX
    return rgb


def resize_png_sequence(src_dir: Path, dest: Path) -> None:
    pngs = sorted(src_dir.glob('*.png'), key=sort_key)
    if not pngs:
        raise RuntimeError(f'目录内无 PNG: {src_dir}')

    frames = [
        rgba_to_palette(
            Image.open(p).convert('RGBA').resize((SIZE, SIZE), Image.Resampling.LANCZOS)
        )
        for p in pngs
    ]

    dest.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        dest,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        disposal=2,
        optimize=False,
        transparency=TRANSPARENT_INDEX,
    )
    print(f'{src_dir.name}/ → {dest.name}  ({len(frames)} 帧, {SIZE}×{SIZE})')


def main() -> None:
    if not SRC_DIR.is_dir():
        print(f'源目录不存在: {SRC_DIR}', file=sys.stderr)
        sys.exit(1)

    for folder_name, out_name in MAPPING.items():
        src = SRC_DIR / folder_name
        if not src.is_dir():
            print(f'缺少源目录: {src}', file=sys.stderr)
            sys.exit(1)
        resize_png_sequence(src, OUT_DIR / out_name)

    print('完成 →', OUT_DIR)


if __name__ == '__main__':
    main()
